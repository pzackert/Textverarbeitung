Unstrukturiertes Konzept
Den aktuellen Ist-Zustand von dem Frontend findest du hier. Einmal bitte durchlesen.
/Users/patrick.zackert/Workspace/masterprojekt/option_2_platform/docs/ist_stand_antragsverarbeitung.md

Okay, lassen wir uns als nächstes auf den Bereich gehen, um die Anträge zu bearbeiten. Wir haben also einmal eine Seite, die Antragsübersicht, und dann können wir von der Antragsübersicht in die Anträge springen. Hier ein Beispiel.
Übersicht
http://localhost:8000/projects
nach
Antrag bsp a
http://localhost:8000/projects/2233657/review
oder ANtrag b
http://localhost:8000/projects/8209d44a/review

Die Anträge werden in dieser Ansicht separat bearbeitet. Einmal bitte auch kontrollieren, Auch die Anbindung weg in Frontend über die API leistet das an der Stelle.
Die Anträge selbst verarbeiten wir, da wird in dem Ist-Zustand entsprechend dokumentiert. Hier wäre wichtig, auch nochmal zu checken, wie ist die Backend- und Frontend-Unbindung, sind die Sachen soweit richtig beschrieben. Unter anderem soll bei der Übersicht der Anträge der gesamte Input-Ordner eigentlich nur gescannt werden. Aktuell ist es so geregelt, dass wir, also hier ist der Input-Ordner, wo alle Anträge abgelegt sind.
/Users/patrick.zackert/Workspace/masterprojekt/option_2_platform/data/input
Und da gibt es noch eine Registrierungs-JSON:
/Users/patrick.zackert/Workspace/masterprojekt/option_2_platform/data/input/registry.json
...die so eine Übersicht darstellt, über alle Projekte, die drin sind. Aber ich weiß nicht, bin ich der Fan davon, das jetzt nochmal in JSON abzulegen, um dort eine Verwaltung zu haben. Weil, also, vielleicht macht die Sinn? Ich weiß nicht, was jetzt besser ist. Ich hätte jetzt gedacht, dass wir mal anfangen, dass wir diese Anträge dann einmal scannen und eigentlich so beschreiben, weil jetzt aktuell gerade sehe ich, in dem Registration JSON ist sicher auch drin, dass da Kriterien geprüft werden, etc. Das entspricht nicht dem, was wir eigentlich haben wollen. Weil pro Projekt, pro Antrag, haben wir einen separaten Ordner, der ist mit einer Nummer versehen, eigentlich eine numerische Nummer, achtstellig. Die wird immer vom System vergeben und angelegt. Und dann befindet sich dort ein Ordner drin, ein annotierter Ordner, ein Upload-Ordner, wo die verschiedenen Teile drin sind. Ich mach dir mal ein Beispiel, wie so ein Antrag aussehen muss.

Antragsordner
/data/projects/id1234/
├── uploads/ (original documents)
├── annotated/ (AI-processed documents with highlights)
├── metadata.json (all application metadata)
├── criteria_results/ (evaluation results per criterion)
└── chat_history.json (conversation log)

Und darin sollte eigentlich nur so die einzelnen Teilen so abgelegt werden. Und für mich macht es eigentlich keinen Sinn jetzt nochmal ein separates, übergreifendes Chasing zu machen, wenn dort ja alle Informationen enthalten sind. Die können ja dann durchgegangen werden eigentlich beim Laden. Da würde ich nochmal gerne deine Meinung zu hören, was jetzt am besten ist, weil eventuell gibt es noch Schiefstände, weil im Ordner wird eventuell was noch verändert irgendwie. Ich glaube, das ist zu groß einfach. Später würden wir das ja eh in den Datenblatt nochmal schreiben. Aber jetzt aktuell würde ich sagen, okay, für jeden Ordner, wenn ein Ordner drin ist, dann gibt es eine bestimmte Form und wenn alle Dateien der Form entsprechen, können dann eingelesen werden. Also wie gesagt, wir warten, dass wir dann maximal diese drei JSON haben können, vom Chat, von den Kriterien-Sites und die Metadaten. Und die Upload-Files und die annotierten Dateien sind die von uns generierten Files, wo eventuell anhand der Kriterien die Stellen gefunden wurden. Da kommen wir nochmal gleich später drauf. So, das wäre erstmal die Sache, die abzuprüfen ist, ob das jetzt so vom Frontend und Backend korrekt vorgesehen ist. Auch von den Schnittstellen her. Wie gesagt, dann als wichtigsten Punkt eigentlich ist, dass wir zeigen ja die Dateien von Original-Ordner im Frontend an. Und wichtig wäre dann eigentlich, wenn wir jetzt die Kriterien prüfen, dann würden wir die Kriterienprüfung, würde ich dann gleich nochmal beschreiben, sollte aber so sein, dass wir sequenziell Kriterien für Kriterien entsprechend durchprüfen. Und die Kriterien sind, wie auch schon beschrieben, im Anführungs-Katalog in den JSON definiert.
/Users/patrick.zackert/Workspace/masterprojekt/option_2_platform/config/criteria_catalog.json
Und die sollten dann abgearbeitet werden, wenn wir das wollen, sozusagen, also mit einer Prüfung. Und dann werden die abgearbeitet. Eventuell müssten wir es so machen, wenn wir mehrere Anträge parallel oder nacheinander abarbeiten wollen, dass wir so eine Queue haben, wo dann sowohl Antrag für Antrag als auch für die Anträge alle Kriterien entsprechend neu geprüft werden. Es kann ja auch sein, dass in der Zwischenzeit neue Kriterien hinzugekommen sind. Genau, soweit. Das einmal. Ja, ich würde Ihnen aber bitten, erstmal so grundsätzlich das nochmal zu prüfen, was beckenseitig vorhanden ist und ob es da Schwachstellen gibt, die wir dann einmal klären sollten in den Anforderungen. Also bitte prüfe einmal den Ist-Zustand und vom beckenseitigen, sodass wir dann in die Analyse einsteigen können. Also nichts coden jetzt an der Stelle, nichts entwickeln, sondern wir prüfen erstmal und gucken, ist das so vorgesehen, dass wir die Anträge, die wir haben, mit den Originaldetailen anhand der Kriterien prüfen können durch das LLM und können wir dann diese Ergebnisse abspeichern auch pro Antrag von dem Katalog und können wir auch annotierte Dateien erzeugen. Also wir wollen ja dann über das RAG-System die Dateien einlesen und dann genau bestimmen, wenn Kriterien zutreffen, wo soll das dann korrekt zu finden sein. Bitte einmal eine kritische Prüfung des Ist-Zustandes aus dem Beckenteil heraus, bitte. Erstelle dazu in DOC auch ein Pfeil, um den Ist-Zustand einmal zu melden und dann lass uns unterhalten darüber, was jetzt schon geht und was nicht geht.

Genau, dann lass uns einmal loslegen. Also, ich würde bei dem Programm Start würde ich gucken, sozusagen, welche Anträge alle vorliegen und wir haben diesen Projektordner, Input-Ordner, als Single Point of Truth, so wie du es richtig gesagt hast. Ich würde nicht auf die Registry.json gehen, Das könnte immer zu sehr fehleranfällig sein und ich möchte, dass beim Programmstart alle Ordner immer durchsucht werden und die Dateien entsprechend sich angehoben werden. Und wichtig wäre für mich, dass wir Das sehr robust bauen und Fehler möglichst vermeiden, das würde heißen, würde ich sagen, dass am Anfang geguckt wird, okay, in dem Ordner:
/Users/patrick.zackert/Workspace/masterprojekt/option_2_platform/data/input
Welche anderen Ordner sind da drinnen und gibt es dort in den Ordnerstrukturen auch einen Uploads-Ordner oder schon die vorhandene Dateistruktur? Wenn die schon vorhanden ist, kann man die ja kurz prüfen, ob die grundsätzlich den Kriterien entspricht. Also eine Vorlage oder ein Muster, das ist valide das Projekt und kann eingelesen werden oder halt nicht. Das würde man irgendwie so tun. Dann würde ich auch bestimmen, dass wir, wenn es keine JSON-Dateien gibt
müssen diese dann entsprechend angelegt werden. Und dazu würde ich immer sagen, dass wir dann iterativ sozusagen diese Metadaten anlegen, einfach das Projekt hochzählen, vielleicht auch aus dem beschriebenen, aus dem Ordner einen Namen, irgendwie die ID vielleicht generieren, je nachdem wie das geht, weil Ordner dürfen eigentlich nicht doppelt benannt werden. Das kommt uns sozusagen zugute, deswegen haben wir pro Ordner ein Antrag, das ist sozusagen das Ziel.
    ├── metadata.json      (all application metadata)
    ├── criteria_responses.json (criteriumsprüfung 
    └── chat_history.json  (conversation log)

Dann würde ich sagen, okay, wir erstellen sozusagen dann nachträglich, wenn die Metadaten JSON nicht vorhanden ist, erstellen wir die, das Kriterium Prüfung oder Criteria Response -> criteria_responses.json .....wird dann auch leer erstellt. Das würde wir da noch keine Prüfung oder so tun, als wenn wir halt noch keinen Kriterium geprüft haben. Das würden wir einfach initial dann so anlegen. Und auch die Chat-Historie würde einfach leer angelegt werden, dass wenn ein, dass ein neuer Chat dann entsprechend, also wie es wenn es ein neuer Chat wäre. Genau. Und so entsprechend robust machen, dass wir das Projekt immer, also die Projektstruktur dann am Anfang beim Programmstart einfach anlesen. Gucken, dass wir die höchste, einfachste Validierung halt haben an der Stelle und nur anhand der Dateien arbeiten. Genauso würden wir dann, also Uploaded Order würden da die Uploaded Dateien drin sein und Annotated Order würden dann auch drin sein. Genau.

Wichtig ist, wie gesagt, dass wir dort KeyBits simpel machen und robust. Das sind die obersten Kriterien. Es gibt eine späte Erweiterung noch, wo wir das ausbauen können, aber erstmal möchte ich das ganz so lassen und einfach reagieren und sagen, okay, wir machen eine ganz simple Prüfung immer der Strukturen und gucken, ob es soweit korrekt ist. Ansonsten müssten wir vielleicht auch, wenn die Projekte nicht eingelesen müssen, neu angelegt werden, ganz simpel erstmal lassen. Aber wichtig ist, im Initialen würde ich immer sagen, ein Projekt würde ich immer so anlegen, entweder aus dem Frontend heraus, das im Frontend so bereitet ist, dass wir sagen, wir legen dort schon diverse Informationen an und Dateien, aber ich könnte die Projekte auch so anlegen, dass ich einfach einen Ordner erstelle, der nicht den Namen hat, eines vorhanden und erstelle den dort unter dem "Uploads" Ordner Meine Dateien, die vom System zu prüfen sind, und alle anderen JSON-Dateien werden dann initial neu erzeugt. Beim Programmstart so, dass wir die größtmögliche Verfügbarkeit von Anträgen schon haben. Also Prüfung wäre, dass wir die Urne durchgehen und die Strukturen so erstellen.

Im Frontend würde es dann wiederum ein bisschen anders laufen. Dort würden wir über den Dialog der Anträge einen neuen Antrag anlegen. Dort haben wir die Sachen, die wir festlegen mit Projektname, Antragsteller, Fördersumme und Beschreibung, die schon drin ist. Und dann würde man ja in den Antrag kommen, der keine Datei aktuell hat. Da würden dann aber auch initial dann darüber die JSON-Dateien alle angelegt werden. Und wir würden dann über diesen Upload-Button im Frontend weitere Dateien in den Uploads online zufügen. Und können dann später über diese Kriterienprüfungsverfahren die annotierten Dateien erstellen und auch die Kriterien prüfen.

Wenn das erst mal soweit klar ist, guckt ihr das Vorgehen nochmal an und beleuchtet das kritisch. Und dann würden wir jetzt einmal ein Konzept erstellen, ein Änderungskonzept, also To-Do's, ein Änderungskonzept, wo wir die Sachen erstmal einfügen. Erstellen erstmal nur das Konzept bitte mit klar definierten Umbaumaßnahmen und den Use Cases. Bitte so einfach und kompakt gehalten, dass man es gut lesen kann. Und dann wird es klar, was wir tun wollen.


Okay, ich gebe dir nochmal schon mal die Frontend-Anweisung auch durch, also bei der Projektübersicht.
http://localhost:8000/projects
Nichts weiter geändert werden. Dort werden wir, wie gesagt, einen Dialog haben für einen neuen Antrag anlegen. Der ist schon vorhanden, aber da muss nichts weiter umgebaut werden. Wir haben ein Suchfeld und wir haben einen Filter, der nach Status des Projektes oder der Förderanträge entsprechend filtern kann. Alle Anträge werden am Anfang als Entwurf gespeichert. Sobald man einmal reinspricht, wird der Status auf Inprüfung versetzt. Erst wenn sie dann wirklich final durch ihren Mitarbeiter abgeschlossen werden, wenn die Kriterien geprüft sind, haben wir abgeschlossen als Status. Das sind die drei Status, die wir haben. Die sind auch schon existent. Dann kommt eine Tabelle, wo entsprechend die Antragsnummer, Projektname, Antragsteller, Fördersumme, Status, Dokumente, letzte Änderungen, Aktionen angezeigt werden. Die gibt es auch schon in der Tabelle, die ist teilweise nur nicht richtig oder fehlerhaft. Der Status ist noch unterschiedlich. Es müsste immer ein Status sein, der entweder Entwurf, Inprüfung oder abgeschlossen heißt. Die Anzahl der Dokumente stimmt nicht überein. Da sollen übrigens nur die Dokumente gezählt werden, die im Uploaded Order drin sind, also die, die der Antragsteller eingereicht hat, nicht die von uns erstellten. Dann haben wir als Aktion, wo wir den Antrag öffnen können. Wir können auch einen Antrag über einen Button löschen. Für mich wäre dann noch eine zusätzliche Aktion notwendig, um einmal die Kriterien alle zu prüfen zu lassen, die dann in eine Queue wiederkommen. Dann könnte man mehrere Anträge prüfen lassen, die dann nacheinander abgearbeitet werden. Dann werden die Kriterien entsprechend geprüft. Die Kriterienprüfung soll so ablaufen, dass wir eine Queue haben, wo wir sagen können, in dem Antrag soll das und das Kriterium geprüft werden. Dann geht das in die Queue und wird vom LMM abgearbeitet. Das kann auch eine bestimmte Zeit dauern. Je nachdem, wie lange das Ergebnis ist, wird das nacheinander abgearbeitet. Diese Queue kann auch entsprechend durch den Frontend abgerufen werden. Die Queue wird aber vom Backend verwaltet. Man kann da nach und nach was draufpacken, sollte durch das Frontend asynchron bedient werden. Dann bekommt man ein Update, solange es läuft oder wenn es fertig ist. So kann man auch im Frontend die Oberfläche immer aktualisieren und muss nicht darauf warten. Es ist nicht geblockt. Das ist wichtig, wenn es um Frontend-Sachen geht. Aktuell sieht das Frontend so aus. Es muss nicht grundsätzlich verändert werden. Es müsste nur noch mal responsive angepasst werden, sodass es auf meinem Screen gut dargestellt und nicht abgeschnitten wird. Da kann ich dir noch mal ein Bild machen.
Bitte erstellen Sie mir übrigens, ich will zwei Dokumente von dir haben, die dann die Anforderungen definieren und das Übergabeprotokoll.
/docs/antrag_backend_requirement.md
/docs/antrag_frontend_requirement.md

In diesen beiden Dateien erstellen wir alle Anforderungen und beschreiben alles, was wir hier besprechen, gerade zu der Antragsübersicht und dem Umbau über die Antragsprüfung. Bitte hier übertrennen zwischen Backend- und Frontend-Anwendungen oder Requirements-Anforderungen. Die Backend-Requirements wirst du dann nachher umbauen, aber lass uns erstmal definieren. Und Frontend wird dann der Frontendler übernehmen, da wirst du die Anforderungen beschreiben und auch ein Übergabefotokopien.

Wichtig ist wieder die superklare, saubere Trennung Backend-Frontend, dass wir die maximale Performance auch haben, dass alles was von Frontend angesprochen wird auch über APIs verfügbar ist und über Backend gemacht wird, sodass es sehr robust und getrennt gebaut ist.



bitte einmal weiter mit. aufnehmen: 
Okay, kommen wir jetzt zum Kriterienprüfung einmal. Ich würde Ihnen jetzt genau beschreiben, was würden wir erwarten bei der Kriteriumsprüfung.
Grundlegend haben wir die Kriterien, die wir zu prüfen haben, in diesem Ordner definiert und liegen:
/Users/patrick.zackert/Workspace/masterprojekt/option_2_platform/config/criteria_catalog.json
Diese Struktur ist immer definiert mit jeweils einer ID, Name, Kategorie, Kurz, Lang, Prompt und Recommended. Die Bedeutung dahinter ist, dass wir immer eine ID, die fortlaufend ist, die sich durch das System vergeben wird, selbst bestimmen. Wir haben einmal einen Namen, den wir beschreiben. Wir haben eine Kategorie, die festgegeben ist, zu wem das Ganze gehört. Wir haben eine Kurzbeschreibung, die z.B. in dieser Tabelle angezeigt wird, oder in den Boxen. Und wir haben eine Langbeschreibung, die länger ist. Und wir haben einen Prompt, und dieser Prompt wird dann durch das LLM ausgeführt. Und Recommended haben wir sozusagen, die muss erfüllt sein, damit die Prüfung dann erfolgreich ist. Das kann auch Falls sein und sozusagen optional sonst sein.


Generell würden wir sagen, dass eine Prüfung, also wie gesagt, wir bauen das ganze System so auf, dass wir sequenziell Anträge mit allen Kriterien prüfen. Also wenn wir sagen, wir haben 10 Kriterien, die zu prüfen sind, und 10 Anträge, dann sind das halt 10 mal 10, also 100 Dinge, die nacheinander sequenziell zu prüfen sind. Und die werden von so einer Queue abgearbeitet. Und es gibt sowohl im Backend als auch im Frontend soll es Optionen geben, wo wir einmal einen gesamten Antrag über alle Kriterien prüfen lassen können, als auch so sagen können, wir möchten nur gerne dieses eine Kriterium nochmal prüfen und nochmal validieren lassen für einen bestimmten Antrag. Also das würden wir machen. Oder an sich wahrscheinlich drei Optionen. Also für alle Anträge alle Kriterien prüfen, für einen Antrag alle Kriterien prüfen oder ein Kriterium für einen Antrag prüfen.

Die Prüfung würde so erfolgen, dass wir als Staatsvoraussetzung einen Antrag haben, der bestimmte Dateien in dem "Uploads" Ordner hat.
Und diese werden dann entsprechend ja beim Antrags, wenn der Antrag, also im Frontend um den Antrag aufrufen, werden die Dateien ja aus dem Uploads Order in das RAG geladen. Hier muss natürlich auch backend-seitig entsprechend das so berücksichtigt werden, dass, bevor wir ein Kriterium prüfen, muss das RAG richtig geladen werden, sodass die Basis dafür da ist, auch die Suche ordentlich zu tun. Und RAG ist ja aufgebaut auf Docling. Wir können alle Dateien ordentlich durchsuchen, mit ordentlichen Angaben auch der Quellen. Das ist wichtig, bitte nochmal hier validieren und prüfen dann.

Also beschreibe ich nochmal hier, wie das von Backend-Seite geht, bevor wir ein Kriterium prüfen, sei es jetzt ein Kriterium oder halt Kriterien für alle Anträge, alle Kriterien, muss immer, wenn wir die Verbindung haben, ein Kriterium für einen Antrag, müssen alle Dateien des Antrages in das ARG geladen werden, die Kriteriumsprüfung erfolgen. Und wenn wir jetzt auf einen anderen Antrag gehen würden, dann müsste die RAG-Basis, die alten Dateien aus dem anderen Antrag entfernt werden und die neuen wieder reingeladen werden, das ist ganz wichtig.
Ablauf bsp :
1. Kriterium K001 für Antrag123 prüfen -> 1. Alle Dateien von Antrag123/uploads ladne in RAG -> LLM prüft Kriterium -> Gibt Antwort  -> Speichern der Antwort /criteria_responses.json
2. Kriterium K002 für Antrag123 prüfen -> Dateien sind shcon geladne in RAG -> LLM prüft Kriterium -> Gibt Antwort  -> Speichern der Antwort /criteria_responses.json
3. Kriterium K001 für Antrag99 prüfen -> Dateien von Antrag123/uploads löschen aus in RAG -> Alle Dateien von Antrag999/uploads ladne in RAG -> LLM prüft Kriterium -> Gibt Antwort  -> Speichern der Antwort /criteria_responses.json

Also was ich sagen will ist, es muss halt immer die richtigen Teilen in das RAG geladen werden von den Antrag und dann können die Kriterien geprüft werden und so wie die Kriterienprüfung in die Queue erfolgt, so werden sie auch abgearbeitet. Also ich kann halt, wie gesagt, einzelne Sachen mal anklicken, dann kommen sie in die Queue rein und werden abgearbeitet sequentiell und asynchron vom Backend Richtung Frontend und somit ladet man entsprechend die richtigen Dateien ins RAG oder löscht sie wieder halt raus, sodass das RAG immer die richtigen Informationen halt hat und die Prüfung dann auch richtig erfolgen kann und es wird auch die Responses werden auch für den jeweiligen Antrag in das richtige JSON geschrieben. Ist das verständlich und verstehst du das, was ich meine?


Dann einmal zur Prüfung an sich, wie das aufgebaut ist. An sich haben wir in den globalen Einstellungen ja so Prompt-Einstellungen für die Kriterienprüfung.
/Users/patrick.zackert/Workspace/masterprojekt/option_2_platform/config/config.yaml

Es gibt bis aktuell einen speziellen  Eintrag dafür .. 
  kriterien_pruefung: "Lies das Kriterium, was zu pr\xFCfen ist, genau und gucke die\
    \ Dokumente durch, ob du dieses Kriterium best\xE4tigen oder ablehnen musst. Antworte\
    \ in dem JSON Format."

Beim Programm Start: Die Idee ist, dass wir am Anfang des ganzen Systemes laden, wird ja das LLM einmal gebrieft über die Einstellung:   global_chat_initial 
Dann sagen wir also schon beim Programmstart dem LLM, was sozusagen seine Aufgabe genau ist und wer was hier tut.
-> hier könntne wir auch alles tun um mit dem globalen chat zu sprechen



ergänze sehr genau die foldennen Anforderugen:
Das ist nochmal Now und jetzt Step-by-Step durchgehen. Vielleicht wird das nochmal klarer, wie der Ablauf sein soll. Also nach dem Systemstart, wo alle Systeme hochgefahren werden, was wir jetzt auch schon implementiert haben, sprich die Engine, Provider, LLM, RG und so weiter, das so alles, das braucht man grundsätzlich auch den Webservice für die Sachen, das so alles sauber getrennt und wird nacheinander hochgefahren. Das ist meine Erwartungshaltung, dass es backend-seitig perfekt funktioniert und das Frontend entsprechend auch gucken kann, sind diese Komponenten separat vorhanden oder nicht. Das ist glaube ich auch schon soweit drin. 

Dann wäre meine Erwartungshaltung Das Initial für den Betrieb, die das Global Knowledge, die globalen Dateien, als Datenbasis für das LLM geladen werden zur Verfügung stehen -> /Users/patrick.zackert/Workspace/masterprojekt/option_2_platform/data/global_knowledge

An dieser Stelle hat aber jetzt noch kein Chat oder irgendwas stattgefunden, sondern einfach die Datenbasis korrekt geladen. Die bleibt doch über den gesamten Programmstart erhalten und drin. Das sind die globalen Inhalte, wo praktisch wir unsere Wissensdatenbank neben dem trainierten Large Language Model immer drin haben.
Wenn wir dann sozusagen erst mal auf die Funktionalität gehen würden des Chats 
http://localhost:8000/chat
In der wie schon gesagt, für jeden Chat ein einzelnes JSON, was historisiert oder persistiert die Infusion speichert. Ein Chat wird immer initialisiert über Die Probleme sind im config /Users/patrick.zackert/Workspace/masterprojekt/option_2_platform/config/config.yaml
Und zwar als allererstes wird jeder separate Chat über diese Initialisierung, den wir festgehalten haben in der Konfiguration "global_chat_initial"
Und wenn das richtigerweise initiiert ist, soll als allererstes für den Benutzer die Begrüßung, die auch in der Konfiguration gespeichert ist -> "begruessung"
Hinweis: ...aufbauen, oder ich weiß nicht, wie du das Wort hast, aber wieder evaluieren, dass man sagen wird, okay, wenn wir die."global_chat_initial" An das LLM schicken, würde ich das gleich sagen. Wenn du alles verstanden hast oder alles richtig ist, antworte bitte nur mit dem Text, der in der "begruessung" Wenn er irgendwelche Probleme hat, soll er die halt antworten, aber wenn alles okay ist, er sowohl die RG-Basis hat und alles korrekt ist, dann soll er gleich mit diesem Satz genauso 1 zu 1 antworten, dann weiß man auch, ob es funktioniert oder nicht funktioniert.
... und dann würde man immer Frage-Antwort-Frage-Antwort erstellen können und machen können. Der Mitarbeiter kann sich mit dem Agent entsprechend unterhalten, der jetzt als Basis einmal die Dateien in dem RAG richtig korrekt hat und wir haben auch in dem jeweiligen Chat ...Kontext richtig eingefügt und das LLM entsprechend vorher schon ein bisschen gebrieft, so dass es immer in seiner Rolle bleibt. Diese ein Sachen, wie gesagt, kann man vorher einmal konfigurieren und einmal sagen und in dem Chat würde dann ein guter Austausch stattfinden. Wichtig zu betonen ist, dass wir bei jeder Anfrage oder jede Frage im Chat von dem Sachbearbeiter, der den Assistenten befragt, immer auch die Antwortrichtlinien, die auch in der Konfirmation hinterlegt sind, mitgeben, damit die Antworten immer in dieser Form stattfinden.
config -> "antwort_richtlinie"
Der konkrete Ablauf: Das System startet mit allen Dateien + Globales wissen in RAG -> chat startet -> vorab an das LLM "global_chat_initial" und -> dann als Antwort von LLM NUR für neuen Chat config "begruessung" vom LLM Assistent an Sachbearbeiter -> Frage vom Sachverarbeiter bsp : "Hallo, wer bist du?" + config "antwort_richtlinie" So dass die Frage mit der Antwortrichtlinie zusammen an das LRM geschickt wird. Die Antwortrichtlinie wird aber nicht im Chat dargestellt. Ich hoffe, so geht das auch. -> Dann kommt die Antwort vom Assistenten LLM zurück. Quellenverweise auf das globale Wissen müssen nicht hier angezeigt werden. Das ist anders als in der Antragsbarriere.
Aber es soll auf jeden Fall das ERG genutzt werden und auch das Wissen in der Antwort berücksichtigt werden. Aber es muss nicht, wie im Antrag, ein Quellenbeweis existieren.

Wenn ich jetzt einen existierenden Chat schon aufmache, wird der Chat mit dem vorhandenen JSON in der Datei geladen, zum Beispiel /Users/patrick.zackert/Workspace/masterprojekt/option_2_platform/data/chats/chat_20251219_151032_280c17bb.json
Es muss keine Begrüßung erfolgen. Wichtig ist nur, dass der Chat dann als Kontextfenster in das LLM geladen wird und darin enthalten sollte er auch normalerweise sein ->  global_chat_initial und auch alle anderne Daten 
Und dann würde man einfach nur warten, bis der Antragsteller wieder eine Frage stellt. Und die Frage, die er stellt, oder eine Antwortfrage, würde dann auch wiederum zusammen + config : "antwort_richtlinie" ...an das LLM gesendet werden und auch wieder in das JSON persistiert und gespeichert werden. Somit haben wir alle Quelle abgedeckt von einem neuen Chat erstellen, einen existierenden weiter benutzen, sozusagen, oder Frage-Antwort-Spiele zu machen, und auch das Löschen würde dann über die Funktion sein, dass man den Chat ja mit dem JSON löscht, und somit haben wir Neuanlegen, Bearbeiten und Löschen drin.

In dieser Stelle würde ich ganz konkret und deutlich einmal das Vorgehen dann beschreiben mit Use Cases und auch gucken, dass man da die Edge Cases entsprechend abbildet. Wichtig ist auch, dass im Backend alles super flüssig strukturiert und ja, einfach sauber abgearbeitet wird und robust ist.

Kommen wir dann einmal zu der... Jetzt werden wir Anträge bearbeiten, das ist ein bisschen anders. Sprich, wir gehen über...http://localhost:8000/projects ...auf ein konkretes Projekt / Antrag http://localhost:8000/projects/8209d44a/review  Das würde aus den Dateien bestehen, aus dem ordner :/Users/patrick.zackert/Workspace/masterprojekt/option_2_platform/data/input/8209d44a

Hier würde vom Frontend-Head auch initial, wenn es ein neuer Antrag ist, ein neuer Chat geladen werden. Da ist genau das gleiche wie beim globalen Chat zu sehen. Und auch wenn ich einen bestehenden Antrag wieder öffne, dann ist das wie beim globalen Chat auch. Die Chat-Datei, die für den Antrag nötig ist, wird geladen. Das ist jetzt auch schon so existent, da muss nichts weiter gemacht werden, das passt zur Zeit. Und wenn ich den Antrag wieder komplett lösche, dann ist ja auch dieser Chat weg. Aber diese Chat-Funktion funktioniert fast gleich, also eigentlich wirklich wesentlich gleich, wie beim globalen Chat.


ABER WICHITG: Wenn ich einen Antrag öffne oder ein Kriterium, für ein Antrag prüfen möchte: muss die RAG Basis vom Antrag entsprechend geladne werden aus in dme Fall bsp : /Users/patrick.zackert/Workspace/masterprojekt/option_2_platform/data/input/8209d44a/uploads
Jeder Antrag hat ja aus seinem Uploads Ordner eigene Dateien. Die müssen immer geladen werden. Ein Chat gehört immer zu einem bestimmten Antrag. Genauso gehört die Kriterienprüfung da auch zu dem Antrag konkret. Die muss vorher vorhanden sein. Das muss auch erkennbar sein, dass diese Basis jetzt geladen wird. Ansonsten würde es halt einen Fehler geben.

Auf dieser Basis von dem Wissen des globalen Chats plus dieser Antragskontext jetzt, also wir haben praktisch das globale Wissen und das Wissen über diesen konkreten Antrag von Arne Thein, jetzt in diesem einen vorhanden. Und wir können damit sozusagen die Kriterien prüfen und den Antrag.

Chat: Wie gesagt, der Chat funktioniert ähnlich gleich, ist auch so, dass z.B. ein neuer Chat, wie beim Global Chat, der initiated wird, wird aber mit einer anderen Dateibasis im RAG, das ist ganz wichtig, also wird erst einmal sozusagen die RAG-Dateien geladen und dann werden die Prompts an den jeweiligen Kontextfenster geladen, geschickt.
ABER Wichtig bei dem Chat, hier habt ihr die Kriterien, ist jetzt der Quellenverweis. Wir haben bei jedem Chat, der vom Assistenten beantwortet wird, wenn es eine Quelle gibt, die sozusagen aus den Dateien des Antrages besteht, also aus dem Chat. -> Dateien von uploads vom Ordner aus dme RAG -> bsp /Users/patrick.zackert/Workspace/masterprojekt/option_2_platform/data/input/8209d44a/uploads/Businessplan.xlsx die dann mit docling bestimtm wurde -> und die Quelle im Chat mit angeben. Das ist auch jetzt schon so im Frontend, du hast es jetzt schon gezeigt. Wichtig, diese Sache wird nicht umgebracht. Diese geht jeden konkreten Datei an. Das ist immer unter jedem Chat, das ist so sehr fotografiert, steht Quellen-Doppelpunkt, und dann steht, wenn es eine Quelle oder mehrere Quellen gibt, werden die jeweils angehabt. Ich kann auf diesen Quellenbezug draufklicken, und dann würde sich im Dokumentenfenster die Quelle, die da diskutiert wird, genau auftun. Somit kann man genau nachweisen, dass Wissen von den LLM, also den Assistenten, beruht auf einer Quelle vom RAG.

Wichtig hier, das Format von Docling muss entsprechend genutzt werden, so dass wir genau sagen können, okay, wo ist genau der Quellenbezug da, in welcher Seite, damit die auch dann genau im Viewer vom Document aufgemacht wird.


Kommen wir jetzt zu den gesonderten Anfragen der Kriteriumsprüfung. Wenn ich ein Kriterium prüfe, ist das ähnlich wie so ein Chat, bloß dass die Antwort ein bestimmtes Format haben muss von dem LLM bzw. den Assistenten.

Wichtig wie gesagt ist für die Prüfung von Kriterien durch das LLM automatisiert oder durch den Assistenten, dass die Dokumentenbasis in das RAG korrekt und vollständig geladen wird und erst dann können alle Kriterien geprüft werden. Kriterien befinden sich wie gesagt in dem JSON.
/Users/patrick.zackert/Workspace/masterprojekt/option_2_platform/config/criteria_catalog.json

  "kriterien": [
    {
      "id": "K001",
      "name": "",
      "kategorie": "",
      "kurz": "",
      "lang": "",
      "prompt": "",
      "recommended": true
    },

Damit ein Kriterium durch das LLM geprüft wird, wird jedes, also sequentiell, nach dem Member, wird, schicken wir immer Das LLM hat zwei Sachen mit. Einmal aus der globalen Konfiguration /Users/patrick.zackert/Workspace/masterprojekt/option_2_platform/config/config.yaml -> den "kriterien_pruefung" und aus dem Kriterienkatalog /Users/patrick.zackert/Workspace/masterprojekt/option_2_platform/config/criteria_catalog.json den "prompt" ...für das jeweilige Kriterium.

Pürfung der kriterien in der Queue z.B. 
Antrag 123 -> Request an das LLM "kriterien_pruefung" + "prompt" vom Krtierium z.B. "id": "K001"
Antrag 123 -> Request an das LLM "kriterien_pruefung" + "prompt" vom Krtierium z.B. "id": "K002"
Antrag 123 -> Request an das LLM "kriterien_pruefung" + "prompt" vom Krtierium z.B. "id": "K003"
....
Antrag 222 -> Request an das LLM "kriterien_pruefung" + "prompt" vom Krtierium z.B. "id": "K001"
Antrag 222 -> Request an das LLM "kriterien_pruefung" + "prompt" vom Krtierium z.B. "id": "K002"
...
Antrag 999 -> Request 
....

Also das ist ein einfaches Frage-Antwort-Spiel, wo wir immer ein Request senden und eine Response wieder bekommen. Die Response ist klar vorgegeben in der "kriterien_pruefung"

So wird der Prompt für die Config "kriterien_pruefung" sein: 
Kritierium KMU
-----------
Du bist ein Fördermittelprüfer der IFB Hamburg mit Spezialisierung auf formale Fördervorraussetzungen gemäß PROFI-Richtlinie(mit angefügt). 
Gib als Antwort/Response als JSON zurück:
{ 
	"status": 
		"rot" | "gelb"| "grün", 
	"begründung": "", #160 zeichen 
	"dokument": "projektantrag.pdf", 
	"referenz": "Seite 3, Absatz 3" | "Zelle A24" 
} 

------------
"prompt" vom Krtierium:
Bitte prüfe folgendes Kriterium: Es muss mind. ein beteiligtes gültiges Unternehmen einer KMU sein. Prüfe die Antrage ob eine KMU vorhanden ist!


_____

Konkret heißt das, wir geben ihm vorher mit den Rahmen, dass er ein Prüfer ist und dieses Kriterium prüfen soll. In der Request würde er sagen, wir brauchen genau ein JSON-Zurück und er soll das entsprechend auffüllen, indem er sagt, der Status ist, wenn diese Anfrage oder dieses Kriterium im Falle z.B. von der KMU hier gültig ist und er findet das, dann wird er grün zurückgeben. Als wirklich ein Wortlaut, Status grün, ansonsten würde er, wenn das nicht gültig ist und er sich sicher auch, dann halt rot und nur wenn er sich unsicher ist, sollte gelb zurückgegeben werden. So würden wir es dann implementieren wollen. Dann soll er entsprechend eine Begründung schreiben, z.B. mit 160 Zeichen maximal, die wir dann auch anzeigen können. Und er soll dann auch das Dokument benennen, das würde ja von Docling kommen So wie wir es praktisch implementiert haben, wo wir das Dokument haben und die Referenz genau. Verstehst du, was ich meine?


Weiteres Bsp ...für das Kriterium. K002:
Wieder wird der Prompt für die Config /Users/patrick.zackert/Workspace/masterprojekt/option_2_platform/config/config.yaml:  "kriterien_pruefung" zusammen mit dem 
/Users/patrick.zackert/Workspace/masterprojekt/option_2_platform/config/criteria_catalog.json "Promt" : Bitte prüfe folgendes Kriterium: Prüfe ob die Vorhaben der Vorgaben der EU-Richtlinie 2019/882 erfüllt (Barrierefreiheitsanforderungen für digitale Produkte und Dienstleistungen, die nach dem 28. Juni 2025 in Verkehr gebracht werden), sofern es gemäß Projektplanung die Entwicklung einer konkreten Produkt- oder Prozessinnovation zum Ziel hat, die in den Geltungsbereich dieser Richtlinie fällt 

Also wir haben praktisch immer die zwei Sachen, die eingegrenzt werden. Wir haben immer die, wo wir genau eingrenzen, was wollen wir praktisch haben, für eine Antwort. Das kommt sozusagen aus der Konfigurationsdatei und dann haben wir aus dem Kriterien-Tatalog der Prompt, der dafür einverwendet wird. Und immer beide Sachen werden immer für eine Kriteriumsprüfung dann an das LLM geschickt. Und dann wichtig ist, dass wir dann mal prüfen, ob das ein JSON-Format ist. Ansonsten versuchen wir es noch einmal, ein neutes Mal, sozusagen sagen, hey, es muss in dem Antwortformat sein und entweder meldet er es richtig zurück oder halt nicht. Dann würden wir, wenn das LLM oder der Assistent das nicht in dem richtigen Format zurückgibt, würden wir halt den Status auf gelb setzen und dann auch vielleicht sagen, hey, keine adäquate Antwort vom Assistenten bekommen oder sowas und auch keine Dokumentenreferenz entsprechend.

Ich denke, dass wir dadurch immer diverse Kriterien über so einen Prompt prüfen können und dann entsprechend die Antworten zurückbekommen. Wichtig ist diese Explizitheit. Das können wir auch genau sagen. Wir können auch dann die Antworten nochmal abändern. Also im anderen Format, wenn wir halt diesen globalen Prompt halt ändern. Oder die Konfiguration ist es ja. Aber somit könnte man immer sequenziell, Step-by-Step, es ist immer eine Frage-Antwort-Spiel. Also genau gleich wie im Chat, bloß dass es halt hier ein bisschen anders nutzen drin ist. Wichtig ist, dass die Sachen nicht im globalen Chat gespeichert werden, sondern dann halt in, das sollte nochmal wichtig sein, hier in dem konkreten Antrag gibt es ja zum Beispiel:
/Users/patrick.zackert/Workspace/masterprojekt/option_2_platform/data/input/8209d44a/criteria_responses.json
... jeweils immer eine JSON-Datei, welche die Kriteriumsprüfung entsprechend beinhaltet. Und da drinnen ist sozusagen nochmal genau gesagt, hey, wie war jetzt die Antwort Was wir jetzt nicht berücksichtigen ist, wenn jetzt die Kriterien sich irgendwie ändern, dann würde erstmal die Antwort genau, also die wir da drin haben, wenn sie schon mal gemacht wurde, Ebola drin sein, aber wir können sie halt neu anstoßen, durch einen neuen Prozess sozusagen, aber wir würden jetzt nicht nochmal prüfen, hey, hat sich irgendwas geändert von der Atomweise, also das müsste neu geprüft werden, das lassen wir mal außen vor.

Ein ganz wichtiger Teil noch. WICHTIG WICHTIG 
Wenn wir ein Kriterium geprüft haben und es gibt sozusagen ein Vorkommen, also ein bestätigtes Vorkommen, dass das Kriterium grün oder gelb ist, wenn man halt sich sicher ist oder so halbwegs unsicher, dann soll Folgendes passieren
Generell werden ja alle Dateien auf der RAG-Basis aus dem Ordner "uploads" pro antrag durchsucht auf basis von der lib docling
z.B.
/Users/patrick.zackert/Workspace/masterprojekt/option_2_platform/data/input/8209d44a/uploads
Wenn wir jetzt ein spezifisches Vorgehen haben, z.B.
/Users/patrick.zackert/Workspace/masterprojekt/option_2_platform/data/input/8209d44a/uploads/IFB_Foerderantrag_Smart_Port_Analytics.pdf
In der Datei ist ein Bezug, eine Quelle, die wir dort entsprechend gefunden haben.
Dann würden wir daraufhin eine annotierte Datei im annotierten Ordner erstellen -> Das System kopiert die Originaldatei und hängt ein Annotiert "_annotated" hinten dran.
bsp:
/Users/patrick.zackert/Workspace/masterprojekt/option_2_platform/data/input/8209d44a/annotated/IFB_Foerderantrag_Smart_Port_Analytics_annotated.pdf
Und in der annotierten Datei wird dann die Stelle markiert. Wir haben das auch schon mal im Backend getestet und durchgespielt, wo das Vorkommen ist, was wir praktisch als Quelle genannt haben.
Das hatten wir auch schon soweit umgesetzt und gebaut. Bitte immer nachgucken. Hier ist ein Beispiel, wie das im Backend abgebildet ist.
     "evidence": [
        {
          "dokument": "Projektskizze_Smart_Port_Analytics.docx",
          "dokument_original_path": "/uploads/Projektskizze_Smart_Port_Analytics.docx",
          "referenz": "Veritaskai 8, 21079 Hamburg-Harburg",
          "text_snippet": "21079",
          "annotated_file": "Projektskizze_Smart_Port_Analytics_annotated.docx",
          "annotated_file_path": "/annotated/Projektskizze_Smart_Port_Analytics_annotated.docx"
        },
        {...
----------

/Users/patrick.zackert/Workspace/masterprojekt/option_2_platform/data/input/8209d44a/criteria_responses.json


-------


Somit haben wir einen guten Prozess, der relativ einfach und simpel ist zur Prüfung, auch für den KI-Assistenten, der eigentlich nur ein LLM ist, mit RAG, das zu tun. Und wir speichern, wie gesagt, die Daten auch immer pro Antrag selbst rein.

Bitte checkt einmal alle Dokumenten, Beziehungen, die ich hier angegeben habe, und die Formate da drinnen. Und ergänzt nochmal die Requirements der back-end und front-end mit richtigen Cases, damit wir das richtig, also gerade auch im front-end extrem durchprüfen. Was ist wo? Ist das halt drinnen? Was soll halt darüber kommen? Und prüft einmal das Vorgehen, ob das so valide ist und ob das so funktioniert. Und stellen wir Rückfragen, wenn das jetzt hier Quatsch ist, wenn wir das nicht so umbauen können. Da bitte einmal wirklich back-end-seitig richtig prüfen, ob diese Art mal so funktioniert.
Ich will jetzt einmal wirklich gründlich prüfen, ob dieses ganze Vorgehen genau so existieren kann und robust laufen kann. Das will ich wirklich so auch... Ich will das einmal, dass das komplett durchgecheckt wird. Ist das die Antwort, die wir von den Systemen bekommen, erwarten, durch die ganzen Sachen, die wir implementiert haben? Und ich will das dann immer komplett trennen, dass alle Use Cases aufgebaut werden und dann einmal backend-seitig komplett getestet werden und frontend-seitig
 
Prüfe jetzt sorgfältig die gesamte Idee, die gesamte Struktur nochmal komplett. Das Ganze vorgehen, ganz minutiös, und schreibt die Anforderungen sehr detailliert und gut runter, sowohl für Backend als auch für Frontend. Prüfe sehr gewissenhaft. Nun schreibt nur die Anforderungen.

Hast du wirklich jede Detail, die wir jetzt schon mal hatten und die ich so als Quelle benannt habe und die JSON-Strukturen genau geprüft und geguckt, kann das genau umgesetzt werden und was muss genau umgebaut werden, damit das solide und alles funktioniert? Ich finde die Anforderungen vom Backend und Frontend noch, also ich hoffe, dass das alles drin ist, aber dass es wirklich exakt genau beschrieben ist. Ich habe mir sehr viel Mühe gegeben mit dem kompletten Beschreiben, sodass wir es bestmöglich auch im Frontend und Backend seitlich implementieren können.
Wenn alles wirklich passt, dann würde ich sagen, legt mit dem Backend los. Implementiert vollständig alle Backend-Anforderungen, die wir haben. Und schreibt das sozusagen auch in verschiedenen Phasen nochmal. Aber implementiert erstmal vollständig alles, was wir gemacht haben. Und im Frontend würde ich ein Übergabeprotokoll haben, wo wir sagen, okay, das haben wir umgebaut, das haben wir umgebaut, das haben wir umgebaut. Und das wird dann nacheinander alles implementiert und umgebaut. Das ist ganz wichtig. Und Frontend-seitig würde ich auch nochmal, schreibt nochmal dazu, dass wir vom Design eigentlich keine Umbauarbeiten machen. Und das soll genau so weiter aussehen. Es muss meiner Meinung nach im Frontend erstmal keine Anpassung vorgenommen werden. Da existiert, wie gesagt, der Chat schon, es existiert der Kriterien-Kanalog. Nur im äußersten Fall soll er dann im Frontend mich informieren, wenn etwas nicht passt. Ansonsten würden wir erstmal das Frontend soweit lassen. Mir geht es nur um das Vorgehen, um das, wie sozusagen wird diese Kriteriumsprüfung gemacht und wie wird damit angegangen. Dass wir dann entsprechend damit agieren und gucken, okay, was passiert genau, wenn man, ja, die Funktionalität ist halt nicht beschrieben. Was muss dann passiert werden? Im Frontend würden wir dann später einmal noch sagen, bzw. im Frontend würde ich sagen, wenn alles dann soweit durchgekürzt und prüfiert ist, soll er mir nochmal sagen, welche Funktionalitäten er im Frontend vielleicht anpassen würde, also im Design, um die Sachen dann darzustellen, wenn es notwendig ist. Das soll er mir dann auch nochmal sagen. Ansonsten, du kürzest dich jetzt ein bisschen weggängsseitig und validierst bitte den gesamten Prozess. 

Ich möchte, dass du das einmal auch alles testest, sehr genau. Und dann, final, will ich, dass du es testest, im weggenseitig, anhand der Anträge.
/Users/patrick.zackert/Workspace/masterprojekt/option_2_platform/data/input/8209d44a
und 
/Users/patrick.zackert/Workspace/masterprojekt/option_2_platform/data/input/14435678
Dazu musst du die Dateien aus den annotierten Ordner herauslöschen auf jeden Fall, damit da auch die Neuen erstellt werden und du musst, glaube ich, nochmal den Kriterienkatalog entsprechend etwas anpassen, wahrscheinlich, nochmal durchgucken, dass das von der Idee her so passt und, also von den Prompts her nur, nur die Prompts zu entsprechen, und auch nochmal in den globalen Settings muss für den Prompt
/Users/patrick.zackert/Workspace/masterprojekt/option_2_platform/config/config.yaml
 ->   kriterien_pruefung: 
...sehr entsprechend angepasst werden, damit wir genau diese Sachen mitgeben, dass das Ausgabeformat ist. Hier so ein Beispiel, das ist auch noch falsch, aber das muss korrigiert werden von dir.
bsp 
"Du bist ein Fördermittelprüfer der IFB Hamburg mit Spezialisierung auf formale Fördervorraussetzungen gemäß PROFI-Richtlinie(mit angefügt). 
Gib als Antwort/Response als JSON zurück:
{ 
	"status": 
		"rot" | "gelb"| "grün", 
	"begründung": "", #160 zeichen 
	"dokument": "projektantrag.pdf", 
	"referenz": "Seite 3, Absatz 3" | "Zelle A24" 
} "

Wichtig ist, dass der vollständige Backend-Test von dir gemacht wird, anhand von Tests, die du selber definierst generell und alles durchspielst, und das dann bereitsteht. Ich werde das an den zwei existierenden Anträgen auch so von dir durchgespielt haben, dass wir das dann später im Frontend auch exakt so darstellen können. Wichtig ist, glaube ich, dass die Antwort-Option an diesen JSON sein muss, und als Status soll halt nur Rot, Gelb oder Grün als Antwort kommen, mit einer Begründung, 160 Zeichen maximal, und die Dokumentenreferenz, wie auch immer sie geartet ist, sodass das dann verwendet werden kann und so abgespeichert werden kann. Ich glaube, das ist gerade noch nicht gleich, wie wir es auf dem  criteria_responses.json  Pro-Antra-Absparherren, aber es sollte dann dementsprechend angepasst werden. Wichtig ist, dass... Also du sollst ja logisch durchdenken komplett, ob das so funktioniert. Nach meinem Dafürhören finde ich es gut, weil ich genau denke, okay, das kann man so sequentiell abarbeiten. Aber da erwarte ich von dir genaue Prüfungen und das dann jetzt loszulegen und vollständig soweit zu implementieren.
LOS!