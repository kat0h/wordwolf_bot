import random


class WordWolf:
    def __init__(self, odai, wolfNum, players):
        _odai = random.sample(odai, len(odai))
        self.odai_citizen = _odai[0]
        self.odai_wolf = _odai[1]
        self.players = []
        for player in players:
            self.players.append({"player": player, "isWolf": False})
        for i in random.sample([i for i in range(len(players))], wolfNum):
            self.players[i]["isWolf"] = True

    def start(self):
        print("ゲームを開始")
        print("人狼のお題 {}".format(self.odai_wolf))
        print("市民のお題 {}".format(self.odai_citizen))
        print("プレイヤー一覧")
        for player in self.players:
            if player["isWolf"]:
                odai = self.odai_wolf
            else:
                odai = self.odai_citizen
            print("プレイヤー: {}	お題: {}".format(player["player"], odai))


if __name__ == "__main__":
    wolf = WordWolf(("vim", "emacs"), 2, ["A", "B", "C", "D", "E"])
    wolf.start()
