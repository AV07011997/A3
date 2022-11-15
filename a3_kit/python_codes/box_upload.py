from boxsdk import DevelopmentClient
from boxsdk import Client

client = DevelopmentClient()
cd
user_id = '10762790373'

bank_folder_id = '134513615428'

itr_folder_id = '134518422575'

#new_file = client.folder(folder_id).upload('D:\\bank\\')

new_file = client.folder(bank_folder_id).upload(r'D:\prudhvi\sources-a3-kit\Scanned-files\KOTAK\42.pdf')