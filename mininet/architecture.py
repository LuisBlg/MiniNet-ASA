"""Modèle d'assemblage : composants, ports, connecteurs et contrats.

Chaque liaison CALL connecte un port requis à un port fourni. Les noms
sont identiques dans le code, le modèle ACME et la matrice générée.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Call:
    name: str
    consumer: str
    required: str
    provider: str
    provided: str
    operations: tuple[str, ...]

COMPONENTS = {
    'Storage': 'storage.Storage',
    'UserManager': 'users.UserManager',
    'FriendManager': 'friends.FriendManager',
    'PostManager': 'posts.PostManager',
    'MessageService': 'messages.MessageService',
    'NotificationService': 'notifications.NotificationService',
    'ConsoleUI': 'console.ConsoleUI',
}
CALLS = (
    Call('user_store','UserManager','store','Storage','users_api',('create_user','credentials','list_users','user_name')),
    Call('friend_store','FriendManager','store','Storage','friends_api',('user_id','add_friend','remove_friend','list_friends')),
    Call('post_store','PostManager','store','Storage','posts_api',('create_post','feed','image')),
    Call('message_store','MessageService','store','Storage','messages_api',('user_id','user_name','create_message','messages')),
    Call('ui_users','ConsoleUI','users','UserManager','api',('register','authenticate','list_users','name')),
    Call('ui_friends','ConsoleUI','friends','FriendManager','api',('add','remove','list')),
    Call('ui_posts','ConsoleUI','posts','PostManager','api',('publish_text','publish_link','publish_image','feed','export_image')),
    Call('ui_messages','ConsoleUI','messages','MessageService','api',('send','history')),
    Call('ui_notifications','ConsoleUI','notifications','NotificationService','api',('take',)),
)
# Un connecteur de type publish/subscribe, deux rôles et deux attaches.
EVENT = ('message_bus','MessageService','events','NotificationService','on_message')
