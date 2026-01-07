document.addEventListener('DOMContentLoaded', () => {
    const carousel = document.querySelector('.carousel');
    const cards = Array.from(document.querySelectorAll('.card'));
    const totalCards = cards.length;
    const restartButton = document.getElementById('restart-button');

    let currentStep = 0; // 0-based index of active card
    let isError = false;
    let pollTimer = null;

    // --- 3D Positioning Logic (Giant Wheel) ---
    function updateCarousel() {
        const radius = 600; // Giant wheel radius
        const theta = 20;   // Degrees per card

        cards.forEach((card, index) => {
            const offset = index - currentStep;

            // Calculate angle for the wheel
            const angle = offset * -theta;

            // Apple-style smooth ease: High precision transform
            // Position on the wheel circumference
            // rotateX moves it along the vertical circle
            // translateZ pushes it out to the radius
            let transform = `rotateX(${angle}deg) translateZ(${radius}px)`;

            // Visibility adjustments
            let opacity = 1;
            let blur = 0;

            // Fade out and blur distant cards
            const absOffset = Math.abs(offset);
            if (absOffset > 0) {
                opacity = Math.max(0, 1 - (absOffset * 0.25));
                blur = absOffset * 3;
            }

            // Apply styles
            card.style.transform = transform;
            card.style.opacity = opacity;
            card.style.filter = `blur(${blur}px)`;
            card.style.zIndex = 100 - absOffset; // Ensure active card is on top

            if (offset === 0) {
                card.classList.add('active');
                card.classList.remove('done');
            } else if (offset < 0) {
                card.classList.remove('active');
                card.classList.add('done');
            } else {
                card.classList.remove('active', 'done');
            }
        });
    }

    // --- State Update Logic ---
    function updateCard(index, data) {
        if (!data) return;

        const card = cards[index];
        const indicator = card.querySelector('.status-indicator');
        const statusText = card.querySelector('.status-text');
        const timestamp = card.querySelector('.timestamp');
        const progress = card.querySelector('.progress-bar');

        // Update Status Indicator
        indicator.className = `status-indicator ${data.status}`;

        // Update Text
        statusText.textContent = data.message || data.status;

        // Update Progress
        if (progress) {
            progress.style.width = `${data.progress}%`;
        }

        // Update Duration if done
        if (data.status === 'ready' && data.duration_sec) {
            timestamp.textContent = `${data.duration_sec}s`;
        }

        // Handle Error Visuals
        if (data.status === 'error') {
            card.classList.add('border-red-500');
            // NOTE: We do NOT set isError=true here, because a single component error (like fallback)
            // should not stop the entire system polling.
        }
    }

    // --- Polling Logic ---
    async function pollStatus() {
        if (isError) return; // Stop polling only on global error

        try {
            const res = await fetch('/api/system/status');
            const data = await res.json();

            // Update all cards
            // Map component names to indices: 0=Scanner, 1=Provider, 2=VectorDB, 3=LLM, 4=RAG, 5=Projects
            const map = {
                'model_scanner': 0,
                'ai_provider': 1,
                'vector_store': 2,
                'llm_loading': 3,
                'global_knowledge': 4,
                'project_healing': 5
            };

            data.components.forEach(comp => {
                const idx = map[comp.name];
                if (idx !== undefined) {
                    updateCard(idx, comp);
                }
            });

            // Update Header Status
            const headerP = document.querySelector('.startup-header p');
            if (headerP) headerP.textContent = data.current;

            // Global Status Handling
            if (data.status === 'ready' || data.status === 'degraded') {
                sessionStorage.setItem('startupStatus', JSON.stringify({
                    status: data.status,
                    message: data.current
                }));
                if (pollTimer) clearInterval(pollTimer);
                setTimeout(() => {
                    window.location.href = '/';
                }, 800);
            } else if (data.status === 'error') {
                isError = true;
                const headerH1 = document.querySelector('.startup-header h1');
                if (headerH1) {
                    headerH1.textContent = "Fehler beim Start";
                    headerH1.style.color = "#ef4444";
                }
                if (restartButton) restartButton.style.display = 'inline-flex';
            } else {
                // Update Carousel Step
                if (data.step > 0) {
                    currentStep = data.step - 1; // 1-based to 0-based
                    if (currentStep >= totalCards) currentStep = totalCards - 1;
                    updateCarousel();
                }
            }

        } catch (e) {
            console.error("Polling failed", e);
        }
    }

    // --- Init ---
    // Check if we need to trigger startup
    fetch('/api/system/status').then(r => r.json()).then(data => {
        const urlParams = new URLSearchParams(window.location.search);
        const forceRestart = urlParams.get('restart') === 'true';

        // Trigger startup ONLY if forced OR if system is in initial state
        if (forceRestart || data.status === 'initializing' || data.status === 'pending') {
            fetch('/api/system/startup', { method: 'POST' });
        } else if (data.status === 'ready' || data.status === 'degraded') {
            sessionStorage.setItem('startupStatus', JSON.stringify({
                status: data.status,
                message: data.current
            }));
            window.location.href = '/';
            return;
        }

        updateCarousel(); // Initial render
        pollTimer = setInterval(pollStatus, 1000);
    });

    if (restartButton) {
        restartButton.addEventListener('click', async (e) => {
            e.preventDefault();
            restartButton.disabled = true;
            restartButton.textContent = 'Starte neu...';
            restartButton.style.display = 'none';
            isError = false;
            try {
                await fetch('/api/system/startup', { method: 'POST' });
                if (pollTimer) clearInterval(pollTimer);
                pollTimer = setInterval(pollStatus, 1000);
            } catch (err) {
                restartButton.textContent = 'Erneut versuchen';
                restartButton.disabled = false;
            }
        });
    }

});
