
import vk_api
user="+380977817853"
pwd='ehteropctel'
client_id = 52882447
client_secret = '3EazsLLc5c5n4yI72OTC'
s2= 'b014e2f1b014e2f1b014e2f153b3320efebb014b014e2f1d77d75ce8e69f01233b236b5'
vk_session = vk_api.VkApi(user, pwd, app_id=client_id)
vk_session.auth()
pass