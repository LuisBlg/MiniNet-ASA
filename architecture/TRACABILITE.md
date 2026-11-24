# Traçabilité : architecture → code

Générée depuis `mininet/architecture.py`. Les ports requis sont les attributs injectés ; les ports fournis sont des ensembles nommés de méthodes exposées par le connecteur.

## Composants

| Composant ACME | Module et classe Python |
|---|---|
| `Storage` | `mininet/components/storage.py` / `Storage` |
| `UserManager` | `mininet/components/users.py` / `UserManager` |
| `FriendManager` | `mininet/components/friends.py` / `FriendManager` |
| `PostManager` | `mininet/components/posts.py` / `PostManager` |
| `MessageService` | `mininet/components/messages.py` / `MessageService` |
| `NotificationService` | `mininet/components/notifications.py` / `NotificationService` |
| `ConsoleUI` | `mininet/components/console.py` / `ConsoleUI` |

## Connecteurs et ports

| Connecteur | Port requis / rôle caller | Port fourni / rôle callee | Opérations |
|---|---|---|---|
| `user_store` | `UserManager.store` | `Storage.users_api` | `create_user`, `credentials`, `list_users`, `user_name` |
| `friend_store` | `FriendManager.store` | `Storage.friends_api` | `user_id`, `add_friend`, `remove_friend`, `list_friends` |
| `post_store` | `PostManager.store` | `Storage.posts_api` | `create_post`, `feed`, `image` |
| `message_store` | `MessageService.store` | `Storage.messages_api` | `user_id`, `user_name`, `create_message`, `messages` |
| `ui_users` | `ConsoleUI.users` | `UserManager.api` | `register`, `authenticate`, `list_users`, `name` |
| `ui_friends` | `ConsoleUI.friends` | `FriendManager.api` | `add`, `remove`, `list` |
| `ui_posts` | `ConsoleUI.posts` | `PostManager.api` | `publish_text`, `publish_link`, `publish_image`, `feed`, `export_image` |
| `ui_messages` | `ConsoleUI.messages` | `MessageService.api` | `send`, `history` |
| `ui_notifications` | `ConsoleUI.notifications` | `NotificationService.api` | `take` |

`message_bus` : `MessageService.events` (publisher) → `NotificationService.on_message` (subscriber), événement `MessageSent` ; `PublisherPort`, `MessageBus` dans `mininet/connectors.py`. Les neuf autres connecteurs sont des instances de `ProcedureCall`. L’assemblage est réalisé dans `mininet/assembly.py`.
