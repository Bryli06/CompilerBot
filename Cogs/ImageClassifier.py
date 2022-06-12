import numpy as np
from discord.ext import commands
from PIL import Image
import requests
from io import BytesIO
from nsfw_model import nsfwDrawing as nd
from nsfw_model import process
DeleteCutoff=0.3
class ImageClassifier(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.model = nd.make_model()
#        self.api = AppPixivAPI()
#        self.api.set_auth("","")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        value = 0
        for attachment in message.attachments:
            image = process.preprocess_image(Image.open(BytesIO(requests.get(attachment.url).content)), process.Preprocessing.YAHOO)
            value = max(value, self.model.predict(np.expand_dims(image, axis=0))[0][1])
        for attachment in message.embeds:
            if attachment.thumbnail:
                image = process.preprocess_image(Image.open(BytesIO(requests.get(attachment.thumbnail.url).content)), process.Preprocessing.YAHOO)
                value = self.model.predict(np.expand_dims(image,axis=0))[0][1]

            if attachment.image:
                image = process.preprocess_image(Image.open(BytesIO(requests.get(attachment.image.url).content)), process.Preprocessing.YAHOO)
                value = self.model.predict(np.expand_dims(image,axis=0))[0][1]
        '''content = message.content
        if "https://www.pixiv.net/en/artworks/" in content:
            pixiv_id = int(
                content[content.index("https://www.pixiv.net/en/artworks/") + len("https://www.pixiv.net/en/artworks/"):])
            print(pixiv_id)
            if pixiv_id:
                url = "https://www.pixiv.net/member_illust.php?mode=medium&illust_id=" + str(pixiv_id)
                print(url)
                image = n2.preprocess_image(Image.open(BytesIO(requests.get(url).content)), n2.Preprocessing.YAHOO)
                value = self.model.predict(np.expand_dims(image, axis=0))[0][1] '''
        if value > DeleteCutoff:
            await message.delete()
            await message.channel.send(content = f"deleted with value {value}")
        elif value!=0:
            await message.channel.send(content = f"Safe with value {value}")

    @commands.Cog.listener()
    async def on_message_edit(self, message_before, message):
        if message.author == self.bot.user:
            return
        value = 0
        for attachment in message.embeds:
            if attachment.thumbnail:
                image = process.preprocess_image(Image.open(BytesIO(requests.get(attachment.thumbnail.url).content)),
                                            process.Preprocessing.YAHOO)
                value = self.model.predict(np.expand_dims(image, axis=0))[0][1]

            if attachment.image:
                image = process.preprocess_image(Image.open(BytesIO(requests.get(attachment.image.url).content)),
                                            process.Preprocessing.YAHOO)
                value = self.model.predict(np.expand_dims(image, axis=0))[0][1]

        if value > DeleteCutoff:
            await message.delete()
            await message.channel.send(content=f"deleted with value {value}")
        elif value !=0:
            await message.channel.send(content=f"Safe with value {value}")
def setup(bot):
    bot.add_cog(ImageClassifier(bot))
