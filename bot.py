import discord
import asyncio
import enum
import random

import util
import game
import data

TOKEN = util.getenv('DISCORD_TOKEN')
client = discord.Client()


class BotStates(enum.Enum):
    Start = enum.auto()
    Setting_wolf = enum.auto()
    Setting_wolf_wait = enum.auto()
    Setting_time = enum.auto()
    Setting_time_wait = enum.auto()
    Setting_varification = enum.auto()
    Setting_varification_wait = enum.auto()
    Game = enum.auto()
    GameOver = enum.auto()
    GameOver_wait = enum.auto()
    End = enum.auto()


class BotState:
    def __init__(self):
        self.state = BotStates.Start
        self.mes = None
        self.rule = {}
        self.getOdai()
        self.game_task = None

    def getOdai(self):
        self.odai = data.getData()

    async def on_message(self, message):
        # 初期化(不十分な気もする。。。)
        if message.content == '!wordwolf':
            mes = []
            mes.append('🐺 ワードウルフ')
            self.channel = message.channel

            if self.game_task is not None:
                self.game_task.cancel()
            members = []
            if message.author.voice is not None:
                for i in message.author.voice.channel.members:
                    if not (i.bot or i.voice.self_mute):
                        members.append(i)
            if len(members) <= 1:
                mes.append('⚠️参加人数が足りません..')
                await self.channel.send('\n'.join(mes))
                self.state = BotStates.End
            else:
                self.state = BotStates.Setting_wolf
                self.members = members
                self.mes = None
                self.rule = {}
                await self.channel.send('\n'.join(mes))
                await self.update()

    async def on_raw_reaction_add(self, payload):
        # ウルフの人数入力待ち
        if (self.state == BotStates.Setting_wolf_wait
                and payload.message_id == self.mes.id):
            self.rule['wolfNum'] = util.emoji2num(payload.emoji.name)
            self.state = BotStates.Setting_time
            await self.update()
        # 議論時間入力待ち
        elif (self.state == BotStates.Setting_time_wait
                and payload.message_id == self.mes.id):
            self.rule['time'] = util.emoji2num(payload.emoji.name)
            self.state = BotStates.Setting_varification
            await self.update()
        # 確認待ち
        elif (self.state == BotStates.Setting_varification_wait
                and payload.message_id == self.mes.id):
            if payload.emoji.name == '🆗':
                await self.channel.send('💨 ゲームを開始します!DMを確認してください')
                self.state = BotStates.Game
            elif payload.emoji.name == '🆖':
                self.mes = await self.channel.send('🔧 再設定します')
                self.state = BotStates.Setting_wolf
            await self.update()
        # 結果発表待ち
        elif (self.state == BotStates.GameOver_wait
              and payload.message_id == self.mes.id):
            mes = []
            mes.append("🎉 結果発表")
            mes.append('```')
            mes.append('ウルフのお題 {}'.format(self.game.odai_wolf))
            mes.append('市民のお題 {}'.format(self.game.odai_citizen))
            for player in self.game.players:
                if player["isWolf"]:
                    odai = self.game.odai_wolf
                else:
                    odai = self.game.odai_citizen
                mes.append('プレイヤー： {} お題： {}'.format(player['player'], odai))
            mes.append('```')
            await self.channel.send('\n'.join(mes))
            mes = await self.channel.send("❓ 再戦しますか？")
            self.mes = mes
            await mes.add_reaction("🆗")
            await mes.add_reaction("🆖")
            self.state = BotStates.End
        elif (self.state == BotStates.End
                and payload.message_id == self.mes.id):
            if payload.emoji.name == '🆗':
                await self.channel.send('♻️ 再戦します。DMを確認してください')
                self.state = BotStates.Game
                await self.update()
            elif payload.emoji.name == '🆖':
                self.mes = await self.channel.send('🏁 終了します')

    async def update(self):
        # ウルフの人数を設定
        if self.state == BotStates.Setting_wolf:
            mes = await self.channel.send('🐺 ウルフの人数を決定してください')
            for i in range(len(self.members) - 1):
                await mes.add_reaction(util.num2emoji(i + 1))
            self.mes = mes
            self.state = BotStates.Setting_wolf_wait
        # 議論時間を設定
        elif self.state == BotStates.Setting_time:
            mes = await self.channel.send('⏰ 議論時間を決定してください')
            for i in range(1, 5):
                await mes.add_reaction(util.num2emoji(i))
            self.mes = mes
            self.state = BotStates.Setting_time_wait
        # 設定を確認
        elif self.state == BotStates.Setting_varification:
            mes = await self.channel.send(
                    '\n'.join([
                            '❓ 以下の設定でゲームをスタートしてもよろしいですか？',
                            '```',
                            'ウルフの数： {}人',
                            '議論時間： {}分',
                            '参加者： {}',
                            '```'
                        ])
                    .format(self.rule['wolfNum'],
                            self.rule['time'],
                            [i.name for i in self.members]),
                           )
            for i in ['🆗', '🆖']:
                await mes.add_reaction(i)
            self.mes = mes
            self.state = BotStates.Setting_varification_wait
        # ゲーム開始
        elif self.state == BotStates.Game:
            self.game = game.WordWolf(random.sample(self.odai, 1)[0],
                                      self.rule['wolfNum'],
                                      self.members)
            for i in self.game.players:
                if i['isWolf']:
                    odai = self.game.odai_wolf
                else:
                    odai = self.game.odai_citizen
                await i['player'].send('あなたのお題→ 「{}」'.format(odai))
            self.state = BotStates.Game
            self.game_task = asyncio.create_task(self.gameOver())

    # 時間切れになったときに呼ばれる
    async def gameOver(self):
        await asyncio.sleep(self.rule['time'] * 60)
        mes = await self.channel.send('⏳ 議論時間が終了しました！ウルフが決まったら下のボタンを押してください')
        await mes.add_reaction('🐺')
        self.mes = mes
        self.state = BotStates.GameOver_wait
