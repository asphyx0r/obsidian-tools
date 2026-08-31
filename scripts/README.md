# initialize-obsidian-vault-structure.py

Le programme initialise un Vault Obsidian avec la structure de répertoires
ci-dessous. Sauf pour `<racine-du-Vault>/`, tous les chemins sont relatifs à
la racine sélectionnée avec `--root` ou à la racine par défaut du programme.

| Répertoire                                      | Rôle                                                                                                                      |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `<racine-du-Vault>/`                            | Répertoire racine du Vault et point d'ancrage de tous les autres répertoires créés par le programme                       |
| `templates/`                                    | Modèles Markdown réutilisables servant à créer des notes homogènes dans le Vault                                          |
| `notes/`                                        | Racine principale des notes actives, organisées par domaine, usage ou sujet                                               |
| `notes/inbox/`                                  | Notes capturées rapidement et conservées temporairement avant leur classement définitif                                   |
| `notes/fintech/`                                | Notes consacrées à la FinTech et aux sujets bancaires ou financiers associés                                              |
| `notes/work/`                                   | Notes liées à l'activité professionnelle                                                                                  |
| `notes/work/datalog/`                           | Notes professionnelles consacrées à Datalog                                                                               |
| `notes/code/`                                   | Notes, références et extraits classés par technologie de programmation ou de script                                       |
| `notes/code/python/`                            | Notes, références, commandes et extraits de code relatifs à Python                                                        |
| `notes/code/powershell/`                        | Notes, références, commandes et extraits de code relatifs à PowerShell                                                    |
| `notes/code/bash/`                              | Notes, références, commandes et extraits de code relatifs à Bash                                                          |
| `notes/code/sql/`                               | Notes, références, requêtes et extraits relatifs à SQL                                                                    |
| `notes/projects/`                               | Documentation et notes propres aux initiatives suivies dans le Vault                                                      |
| `notes/projects/prompts-source-control/`        | Notes Obsidian consacrées au dépôt `Prompts Source Control`                                                               |
| `notes/hobbies/`                                | Racine des notes consacrées aux loisirs et centres d'intérêt                                                              |
| `notes/hobbies/warhammer/`                      | Notes consacrées à Warhammer et aux sujets associés                                                                       |
| `notes/hobbies/magic-the-gathering/`            | Notes consacrées à Magic: The Gathering                                                                                   |
| `notes/hobbies/graffiti/`                       | Notes consacrées au graffiti et aux sujets associés                                                                       |
| `notes/books/`                                  | Notes et documentation relatives aux livres                                                                               |
| `notes/books/specifications/`                   | Spécifications régissant la structure, les métadonnées ou le traitement des notes relatives aux livres                    |
| `notes/devtools/`                               | Documentation consacrée aux outils de développement, de versionnement et aux contextes de travail                         |
| `notes/devtools/codex/`                         | Notes, références et procédures consacrées à Codex                                                                        |
| `notes/devtools/claude/`                        | Notes, références et procédures consacrées à Claude                                                                       |
| `notes/devtools/git/`                           | Notes, références et procédures consacrées à Git                                                                          |
| `notes/devtools/github/`                        | Notes, références et procédures consacrées à GitHub                                                                       |
| `notes/devtools/vscode/`                        | Notes, références et procédures consacrées à Visual Studio Code                                                           |
| `notes/devtools/tmux/`                          | Notes, références et procédures consacrées à tmux                                                                         |
| `notes/devtools/psmux/`                         | Notes, références et procédures consacrées à psmux                                                                        |
| `notes/tasks/`                                  | Racine des listes et notes servant à gérer les tâches actives                                                             |
| `notes/tasks/daily/`                            | Listes opérationnelles de tâches rattachées à une journée précise                                                         |
| `notes/tasks/backlogs/`                         | Tâches, idées ou actions actives mais non planifiées, à prioriser ou traiter ultérieurement                               |
| `notes/tasks/recurring/`                        | Tâches répétitives définies avec une cadence ou une règle de récurrence                                                   |
| `notes/recipes/`                                | Recettes de cuisine conservées dans le Vault                                                                              |
| `notes/goals/`                                  | Notes consacrées aux objectifs actuellement envisagés ou poursuivis                                                       |
| `attachments/`                                  | Images, documents et autres fichiers joints référencés par les notes du Vault                                             |
| `archive/`                                      | Racine des contenus qui ne sont plus actifs mais doivent être conservés pour leur historique ou leur consultation         |
| `archive/tasks/`                                | Tâches terminées, abandonnées, annulées ou devenues obsolètes, retirées des listes actives                                |
| `archive/goals/`                                | Objectifs qui ne sont plus actifs, afin de conserver leur historique sans encombrer les objectifs courants                |
| `sandbox/`                                      | Notes et fichiers temporaires utilisés pour les essais, expérimentations ou validations avant classement définitif        |
