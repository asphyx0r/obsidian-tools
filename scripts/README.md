# initialize-obsidian-vault-structure.py

Le programme initialise un Vault Obsidian à partir d'un instantané figé des
répertoires du Vault de référence. Il recrée cette structure de façon autonome
à partir de sa liste intégrée. Sauf pour `<racine-du-Vault>/`, tous les chemins
ci-dessous sont relatifs à la racine sélectionnée avec `--root` ou à la racine
par défaut du programme.

| Répertoire                                                                 | Rôle                                                                                                               |
| -------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `<racine-du-Vault>/`                                                       | Répertoire racine du Vault et point d'ancrage de tous les autres répertoires créés par le programme                |
| `templates/`                                                               | Modèles Markdown réutilisables servant à créer des notes homogènes dans le Vault                                   |
| `templates/notes/`                                                         | Modèles de notes classés selon les catégories de notes/                                                            |
| `templates/notes/ai/`                                                      | Modèles consacrés à l’intelligence artificielle hors développement                                                 |
| `templates/notes/ai/chatgpt/`                                              | Modèles pour les usages de ChatGPT hors développement                                                              |
| `templates/notes/books/`                                                   | Modèles pour les notes de livres                                                                                   |
| `templates/notes/devtools/`                                                | Modèles pour les outils de développement                                                                           |
| `templates/notes/devtools/codex/`                                          | Modèles pour les rapports et références Codex                                                                      |
| `templates/notes/devtools/git/`                                            | Modèles pour les références Git et les arborescences de dépôts                                                     |
| `templates/notes/devtools/github/`                                         | Modèles consacrés à GitHub                                                                                         |
| `templates/notes/devtools/github/repositories/`                            | Modèles pour les fiches de dépôts GitHub                                                                           |
| `templates/notes/goals/`                                                   | Modèles pour les objectifs personnels                                                                              |
| `templates/notes/gtd/`                                                     | Modèles pour les listes et revues GTD                                                                              |
| `templates/notes/gtd/weekly-schedules/`                                    | Modèles pour les plannings hebdomadaires                                                                           |
| `templates/notes/hobbies/`                                                 | Modèles de loisirs communs à plusieurs jeux ou catégories                                                          |
| `templates/notes/profiles/`                                                | Modèles pour les notes de profils                                                                                  |
| `templates/notes/recipes/`                                                 | Modèles de recettes et export du template Web Clipper                                                              |
| `templates/notes/tasks/`                                                   | Modèles pour les listes de tâches                                                                                  |
| `templates/notes/tattoo/`                                                  | Modèles consacrés au tatouage                                                                                      |
| `templates/notes/tattoo/inktober/`                                         | Modèles pour les listes annuelles Inktober                                                                         |
| `notes/`                                                                   | Racine principale des notes actives, organisées par domaine, usage ou sujet                                        |
| `notes/inbox/`                                                             | Notes capturées rapidement et conservées temporairement avant leur classement définitif                            |
| `notes/fintech/`                                                           | Notes consacrées à la FinTech et aux sujets bancaires ou financiers associés                                       |
| `notes/work/`                                                              | Notes liées à l'activité professionnelle                                                                           |
| `notes/work/datalog/`                                                      | Notes professionnelles consacrées à Datalog                                                                        |
| `notes/code/`                                                              | Notes, références et extraits classés par technologie de programmation ou de script                                |
| `notes/code/python/`                                                       | Notes, références, commandes et extraits de code relatifs à Python                                                 |
| `notes/code/powershell/`                                                   | Notes, références, commandes et extraits de code relatifs à PowerShell                                             |
| `notes/code/bash/`                                                         | Notes, références, commandes et extraits de code relatifs à Bash                                                   |
| `notes/code/sql/`                                                          | Notes, références, requêtes et extraits relatifs à SQL                                                             |
| `notes/projects/`                                                          | Documentation et notes propres aux initiatives suivies dans le Vault                                               |
| `notes/projects/prompts-source-control/`                                   | Notes Obsidian consacrées au dépôt `Prompts Source Control`                                                        |
| `notes/hobbies/`                                                           | Racine des notes consacrées aux loisirs et centres d'intérêt                                                       |
| `notes/hobbies/warhammer/`                                                 | Notes consacrées à Warhammer et aux sujets associés                                                                |
| `notes/hobbies/warhammer40k/`                                              | Notes consacrées à Warhammer 40,000                                                                                |
| `notes/hobbies/warhammer40k/v11/`                                          | Notes et références Warhammer 40,000 pour v11                                                                      |
| `notes/hobbies/age-of-sigmar/`                                             | Notes consacrées à Age of Sigmar                                                                                   |
| `notes/hobbies/the-old-world/`                                             | Notes consacrées à The Old World                                                                                   |
| `notes/hobbies/magic-the-gathering/`                                       | Notes consacrées à Magic: The Gathering                                                                            |
| `notes/hobbies/graffiti/`                                                  | Notes consacrées au graffiti et aux sujets associés                                                                |
| `notes/books/`                                                             | Notes et documentation relatives aux livres                                                                        |
| `notes/books/specifications/`                                              | Spécifications régissant la structure, les métadonnées ou le traitement des notes relatives aux livres             |
| `notes/ai/`                                                                | Notes consacrées à l'intelligence artificielle, hors programmation et développement                                |
| `notes/ai/chatgpt/`                                                        | Notes, références et usages de ChatGPT, hors programmation et développement                                        |
| `notes/devtools/`                                                          | Documentation consacrée aux outils utilisés principalement dans une activité de développement                      |
| `notes/devtools/codex/`                                                    | Notes, références et procédures consacrées à Codex                                                                 |
| `notes/devtools/claude/`                                                   | Notes, références et procédures consacrées à Claude                                                                |
| `notes/devtools/git/`                                                      | Notes, références et procédures consacrées à Git                                                                   |
| `notes/devtools/github/`                                                   | Notes, références et procédures consacrées à GitHub                                                                |
| `notes/devtools/github/repositories/`                                      | Notes et documentation consacrées aux dépôts GitHub                                                                |
| `notes/devtools/docker/`                                                   | Notes, références et procédures consacrées à Docker                                                                |
| `notes/devtools/vscode/`                                                   | Notes, références et procédures consacrées à Visual Studio Code                                                    |
| `notes/terminal/`                                                          | Notes consacrées aux terminaux, à la saisie de commandes et aux outils CLI                                         |
| `notes/terminal/tmux/`                                                     | Notes, références et procédures consacrées à tmux                                                                  |
| `notes/terminal/psmux/`                                                    | Notes, références et procédures consacrées à psmux                                                                 |
| `notes/system/`                                                            | Notes consacrées aux systèmes d'exploitation                                                                       |
| `notes/system/windows/`                                                    | Notes, références et procédures consacrées à Windows                                                               |
| `notes/system/windows/wsl/`                                                | Notes, références et procédures consacrées au Sous-système Windows pour Linux                                      |
| `notes/obsidian/`                                                          | Notes et références sur l'utilisation d'Obsidian                                                                   |
| `notes/tasks/`                                                             | Racine des listes et notes servant à gérer les tâches actives                                                      |
| `notes/tasks/daily/`                                                       | Listes opérationnelles de tâches rattachées à une journée précise                                                  |
| `notes/tasks/backlogs/`                                                    | Tâches, idées ou actions actives mais non planifiées, à prioriser ou traiter ultérieurement                        |
| `notes/tasks/recurring/`                                                   | Tâches répétitives définies avec une cadence ou une règle de récurrence                                            |
| `notes/recipes/`                                                           | Recettes de cuisine conservées dans le Vault                                                                       |
| `notes/tattoo/`                                                            | Notes consacrées aux tatouages                                                                                     |
| `notes/tattoo/inktober/`                                                   | Listes annuelles de dessins Inktober                                                                               |
| `notes/profiles/`                                                          | Notes consacrées aux profils                                                                                       |
| `notes/goals/`                                                             | Notes consacrées aux objectifs actuellement envisagés ou poursuivis                                                |
| `notes/gtd/`                                                               | Fichiers de tri GTD                                                                                                |
| `notes/gtd/inbox/`                                                         | Éléments recueillis en attente de clarification et de tri selon GTD                                                |
| `notes/gtd/reference/`                                                     | Documents de référence pour la méthode GTD                                                                         |
| `notes/gtd/reference/samples/`                                             | Cas pratiques d'application de la méthode GTD                                                                      |
| `notes/gtd/weekly-schedules/`                                              | Plannings hebdomadaires associés à l'organisation GTD                                                              |
| `notes/health/`                                                            | Notes consacrées à la santé                                                                                        |
| `notes/health/medical/`                                                    | Notes et références sur les sujets médicaux                                                                        |
| `notes/health/nutrition/`                                                  | Notes consacrées à la nutrition et à l'alimentation                                                                |
| `notes/watchlists/`                                                        | Listes de veille et de suivi                                                                                       |
| `attachments/`                                                             | Images, documents et autres fichiers joints référencés par les notes du Vault                                      |
| `attachments/archive/`                                                     | Pièces jointes associées aux contenus archivés                                                                     |
| `attachments/archive/sans-titre-9/`                                        | Pièces jointes associées à l'entrée d'archive `sans-titre-9`                                                       |
| `attachments/notes/`                                                       | Pièces jointes associées aux notes                                                                                 |
| `attachments/notes/devtools/`                                              | Pièces jointes associées aux notes sur les outils de développement                                                 |
| `attachments/notes/devtools/docker/`                                       | Pièces jointes associées aux notes sur Docker                                                                      |
| `attachments/notes/devtools/docker/formation-dokcv2/`                      | Pièces jointes associées à la note `formation-dokcv2`                                                              |
| `attachments/notes/health/`                                                | Pièces jointes associées aux notes sur la santé                                                                    |
| `attachments/notes/health/medical/`                                        | Pièces jointes associées aux notes sur les sujets médicaux                                                         |
| `attachments/notes/health/nutrition/`                                      | Pièces jointes associées aux notes sur la nutrition                                                                |
| `attachments/notes/hobbies/`                                               | Pièces jointes associées aux notes sur les loisirs                                                                 |
| `attachments/notes/hobbies/warhammer40k/`                                  | Pièces jointes associées aux notes sur Warhammer 40,000                                                            |
| `attachments/notes/hobbies/warhammer40k/v11/`                              | Pièces jointes associées aux notes sur la version 11 de Warhammer 40,000                                           |
| `attachments/notes/hobbies/warhammer40k/v11/blood-angels-smooth-slapchop/` | Pièces jointes associées à la note sur la peinture des Blood Angels en smooth slapchop                             |
| `attachments/notes/hobbies/warhammer40k/v11/captain-tycho-s-blood-angels/` | Pièces jointes associées à la note sur les Blood Angels du capitaine Tycho                                         |
| `attachments/notes/profiles/`                                              | Pièces jointes associées aux notes de profils                                                                      |
| `attachments/notes/profiles/hinge/`                                        | Pièces jointes associées aux profils Hinge                                                                         |
| `archive/`                                                                 | Racine des contenus qui ne sont plus actifs mais doivent être conservés pour leur historique ou leur consultation  |
| `archive/tasks/`                                                           | Tâches terminées, abandonnées, annulées ou devenues obsolètes, retirées des listes actives                         |
| `archive/goals/`                                                           | Objectifs qui ne sont plus actifs, afin de conserver leur historique sans encombrer les objectifs courants         |
| `sandbox/`                                                                 | Notes et fichiers temporaires utilisés pour les essais, expérimentations ou validations avant classement définitif |

Les modèles thématiques se trouvent dans `templates/notes/<catégorie>/`. Les
catégories reprennent les domaines de `notes/`, sans duplication systématique
de tous ses sous-répertoires. Les modèles génériques peuvent rester dans
`templates/`. Les pièces jointes sont réparties entre `attachments/archive/`
et `attachments/notes/`. Sous `attachments/notes/`, les dossiers propres à une
note suivent les catégories déclarées dans la liste ci-dessus.

Dans `notes/gtd/`, les fichiers `next-actions.md`, `waiting-for.md`, `someday.md`
et `weekly-review.md` sont à créer par l'utilisateur. Le programme crée aussi
`notes/gtd/weekly-schedules/`, avec un `.gitkeep` si ce sous-répertoire est vide.
Aucun nouveau `.gitkeep` n'est créé dans le parent `notes/gtd/` ; un marqueur
parent déjà présent est conservé sans modification.

Les sous-répertoires vides de `notes/`, ainsi que le répertoire vide
`attachments/notes/profiles/hinge/`, reçoivent un `.gitkeep` vide. Dans
`attachments/`, cette règle s'applique uniquement à Hinge. Le programme
conserve tous les fichiers existants, y compris un éventuel marqueur
`notes/system/windows/.gitkeep` issu d'une initialisation antérieure.

Un Vault neuf comprend 98 répertoires, racine comprise, et 40 fichiers
`.gitkeep` vides. Chaque dossier feuille sous `notes/` en reçoit un, soit 39
au total, et Hinge en reçoit un. L'initialisation crée les répertoires et ces
marqueurs. Le contenu des notes, des modèles et des pièces jointes ainsi que
les réglages du Vault sont hors du périmètre de l'instantané.

Les options `--root` et `-r` exigent un chemin. Une autre option placée à la
suite est refusée. Pour un chemin commençant par un tiret, utiliser
`--root=-nom` ou `--root ./-nom`.

La simulation et l'initialisation partagent une prévalidation complète avant
toute création : types des chemins, ancêtres de la racine, accès observables,
lecture des sous-répertoires de notes et types des `.gitkeep`. Les liens
symboliques et les points de réanalyse Windows sont refusés dans les chemins
gérés et leurs ancêtres, même si leur cible est absente. Les sous-répertoires
personnalisés liés sous `notes/` sont ignorés. Un `.gitkeep` déjà présent doit être
un fichier ordinaire ; les liens et autres types sont refusés.

Les ancêtres manquants nécessaires à la racine sont affichés dans la simulation
et créés lors de l'initialisation, mais ne sont pas inclus dans les compteurs
des répertoires du Vault. Aucun accès en écriture n'est exigé si aucune création
n'est nécessaire.

Le mode `--dry-run` n'écrit aucun fichier de test des permissions. Les contrôles
d'accès ne garantissent pas la réussite des écritures ultérieures : une panne,
un changement de permissions ou une modification concurrente peut interrompre
l'exécution. Le programme signale alors un résultat potentiellement partiel,
sans annuler les créations déjà effectuées. Les codes de sortie sont `0` en cas
de réussite, `1` pour une erreur d'initialisation et `2` pour des arguments
invalides.
