import asyncio
import yaml
import discord

from soundboard import hook


class DiscordSoundboardProxy:

    def __init__(self):
        self.queue = []
        self.client = discord.Client()
        self.hooks = hook.GlobalHookManager()
        self.email = None
        self.password = None
        self.token = None
        self.server = None
        self.channel = None
        self.bot = None

    def configure(self, path):

        stream = open(path, 'r')
        config = yaml.load(stream)

        self.email = config['email']
        self.password = config['password']
        self.server = config['server']
        self.channel = config['channel']
        self.bot = config['bot']

        if not self.email:
            raise ValueError('missing email address')
        if not self.password:
            raise ValueError('missing password')
        if not self.server:
            raise ValueError('missing server name')
        if not self.server:
            raise ValueError('missing server text channel name')
        if not self.bot:
            raise ValueError('missing bot name')

        # parse key bindings in the configuration file

        bindings = config['bindings']
        if bindings is not None:
            for k, v in bindings.items():
                self.register(k, v)

    async def play(self, effect):
        server = self._find_server_by_name(self.server)
        if server is not None:
            channel = self._find_channel_by_name(server, self.channel)
            if channel is not None:
                user = self._find_member_id(server, self.bot)
                msg = user.mention + " " + effect
                print("playing %s" % effect)
                await self.client.send_message(channel, msg)

    def register(self, pattern, effect):
        self.hooks.register(hook.WM_KEYUP, pattern, lambda: self.queue.append(effect))

    def stop(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.client.close())

    def run(self):
        loop = asyncio.get_event_loop()
        try:
            loop.create_task(self._daemon())
            loop.run_until_complete(self.client.login(self.email, self.password))
            loop.run_until_complete(self.client.connect())
        except Exception:
            loop.run_until_complete(self.client.close())
            raise
        finally:
            loop.close()

    async def _daemon(self):
        await self.client.wait_until_ready()
        print('connected to server')
        loop = asyncio.get_event_loop()
        while loop.is_running():
            self.hooks.poll()
            if not self.client.is_closed:
                for effect in self.queue:
                    await self.play(effect)
                self.queue.clear()

    def _find_server_by_name(self, name):
        for s in self.client.servers:
            if s.name == name:
                return s
        return None

    @staticmethod
    def _find_member_id(server, name):
        return server.get_member_named(name)

    @staticmethod
    def _find_channel_by_name(server, name):
        for ch in server.channels:
            if ch.type == discord.ChannelType.text and ch.name == name:
                return ch
        return None

