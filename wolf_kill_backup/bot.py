import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord import Game
from random import choice
import time
import keepalive
#----------------------------------------------------------------------------------------------------------#

client = discord.Client()     #core
bot = commands.Bot(command_prefix='#')

#----------------------------------------------------------------------------------------------------------#

mode=0     #setting

# 0: not started yet
# 1: prepare
# 2: wolves killing
# 3: witch action
# 5: merlin
# 6: hunter
# 7: vote
me=0
namenumdic={}
name=""
nameforwolf=""
hunterdead=0
votetokill=[]
votetoout=[]
jobarr=[[],[],[],[],[]]
ML=[]
wf=0
wfpass=0
healthuesd=0
poisonused=0
healthuesd=0
hunterdead=0
#----------------------------------------------------------------------------------------------------------#

# me: num members
# ML: member
# wf: num wolves
# WL: wolves
# DR: merlins
# HU: the hunter
# VI: the villager
# WI: the witches
# DE: DEAD
#----------------------------------------------------------------------------------------------------------#
#jobarr [WL , DR , HU , WI , VI]
#----------------------------------------------------------------------------------------------------------#
#ML (name, job, state)
#num :  player's number 
#name:  player's name
#job:   player's job
def distribution():
    global me,wf,jobarr,ML
    wf = 3 if me >9 else 2
    tmp=list([ML[i]['num'] for i in range(len(ML))])
    for i in [(3 if me > 9 else 2,"WL",0), #wolves
              (1 if me > 9 else 0,"DR",1), #merlins
              (1,"HU",2),                  #the hunter
              (1,"WI",3)]:                 #the witches
              for x in range(i[0]):                  
                c=choice(tmp)
                ML[c-1]["job"]=i[1]
                jobarr[i[2]].append(ML[c-1]['name'])
                tmp.remove(c)
    for i in tmp:
      jobarr[4].append(ML[i-1]['name'])
      ML[i-1]["job"]="VI"
#----------------------------------------------------------------------------------------------------------#
def check (user,job):
  global namenumdic ,ML
  if ML[namenumdic[user]-1]['job']==job:
    return True
  return False
#----------------------------------------------------------------------------------------------------------#
def reset ():
  global me,ML,jobarr,namenumdic,name,hunterdead,mode,wf,poisonused,healthused,nameforwolf,hunterout
  name=""
  nameforwolf=""
  me=0
  hunterdead=0
  hunterout=0
  namenumdic={}
  jobarr=[[],[],[],[],[]]
  ML=[]
  wf=0
  mode=0
  poisonused=0
  healthused=0

#----------------------------------------------------------------------------------------------------------#
@bot.event
async def on_ready():#open
    print("bot online")
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('|狼人殺|使用"#start"來開使一場遊戲|'))
#----------------------------------------------------------------------------------------------------------#

@bot.command()
async def go(ctx):
    global mode,me,ML,name,wfpass,name,nameforwolf,jobarr
    if mode==1:
        if(me>= 6 and me<=11):
            distribution()
            namegenerate()
            await ch.send('\n開始分配角色......')   
            await jobarr[3][0].send('\n討厭你是女巫')
            await jobarr[2][0].send('\n你槍好大根')
            for i in jobarr[4]:
                await i.send('\n又是村民ㄟ')
            for i in jobarr[0]:
                await i.send('\n臭狼')
                await i.send('\n請選擇要殺的對象  回復:#kill (玩家編號)')
                await i.send(nameforwolf)
            if me>9:
                await jobarr[1][0].send('\n天啊會預言')
            await ch.send('\n分配完成......\n天黑請閉眼\n狼人現身請睜眼')
            mode=2
        else:
            await ch.send('人數不合規定\n請重新輸入"#start"來重啟遊戲')
            reset()
#----------------------------------------------------------------------------------------------------------#
def namegenerate():
  global ML,name,nameforwolf
  for i in range(len(ML)):
    nameforwolf+=str(ML[i]['num']) +"     |      \t" +str (ML[i]['name']) + "     |      \t" +("狼" if str(ML[i]['job'])=="WL" else "")+("已死" if str(ML[i]['job'])=="DE" else "")+"\n"
    name+=str(ML[i]['num']) +"     |      \t" +str (ML[i]['name']) + "     |      \t" +("已死" if str(ML[i]['job'])=="DE" else "")+"\n"

#----------------------------------------------------------------------------------------------------------#
@bot.command()
async def kill(ctx,input:int):
  global ch,WF,WI,mode,name,hunterdead,HU,deadtonight,wfpass,votetokill,w,poisonused,healthuesd,me,jobarr
  deadtonight=[]
  if mode==2:
    if check(ctx.author,"WL"):
      votetokill.append(input)
      wfpass+=1
      if wfpass==wf:
        wfpass=0
        votetokill=[]
        if wf==2 and votetokill[0] == votetokill[1]:
          deadtonight.append(max(votetokill,key=votetokill.count))
          await ch.send("狼人請閉眼......\n女巫現身請睜眼")
          mode=3
          if poisonused==0 or poisonused==0:
            await jobarr[3][0].send(f"昨晚{deadtonight[0]}號被殺了\n請使用#poison (玩家編號)或#health 或 #topass 來行動\n{name}")
          else:
            await jobarr[3][0].send("你的藥水乾掉了\n請使用#topass 來略過")
        else:
          for i in jobarr[0]:
            await i.send("最高票重複\n請重投")
    else:
      await ctx.send("阿就不是狼人在那邊搞")
  else:
    await ctx.send('遊戲階段錯誤')
#----------------------------------------------------------------------------------------------------------#
@bot.command()
async def poison(ctx,input:int):
  global WI,mode,deadtonight,poisonused,me,jobarr,wf
  if mode ==3:
    if check(ctx.author,"WL"):
      if poisonused==0:
        deadtonight.append(input)
        poisonused=1
        if me>9:
          await ch.send("女巫請閉眼......\n預言家現身請睜眼")
          await jobarr[1][0].send(f"請使用 #examine (玩家編號)來查驗身分\n{name}")
          mode=5
        else:
          for i in deadtonight:
            if ML[i-1]["job"] =="HU":
              await ch.send("女巫請閉眼......\n獵人現身請睜眼")
              await jobarr[2][0].send("你死了 請使用#bring (玩家編號)來選擇要帶走的人")
              await jobarr[2][0].send(name)
              mode=6
              hunterdead=1
              break
          if hunterdead==0:
            await ch.send("獵人請閉眼......\n天亮了\n昨晚")
            for i in deadtonight:
              if ML[i-1]['job']=='WL':
                wf-=1
              await ch.send(ML[i-1]['name'])
              ML[i-1]['job']="DE"
              me-=1
            await ch.send("被殺了")
            if wf==0:
              await ch.send("人類勝利")
              reset()
            elif me-wf<=wf:
              await ch.send("狼人勝利")
              reset()
            else:
              await ch.send("遊戲尚未結束請使用 #vote (玩家編號) 來投票")
              await ch.send(name)
              mode=7
      else:
        await ctx.send("你已經用過了") 
    else:
      await ctx.send("阿就不是女巫在那邊搞")
  else:
    await ctx.send('遊戲階段錯誤')

@bot.command()
async def health(ctx):
  global WI,mode,DR,me,name,healthused,hunterdead,deadtonight,jobarr,wf
  if mode==3:
    if check(ctx.author,"WI"):
      if healthused==0:
        deadtonight.remove(deadtonight[0])
        healthused=1
        if me>9:
          await ch.send("女巫請閉眼......\n預言家現身請睜眼")
          await jobarr[1][0].send("請使用 #examine (玩家編號)來查驗身分")
          await jobarr[1][0].send(name)
          mode=5
        else:
          for i in deadtonight:
            if ML[i-1]["job"] =="HU":
              await ch.send("女巫請閉眼......\n獵人現身請睜眼")
              await jobarr[2][0].send("你死了 請使用#bring (玩家編號)來選擇要帶走的人")
              await jobarr[2][0].send(name)
              mode=6
              hunterdead=1
              break
          if hunterdead==0:
            await ch.send("獵人請閉眼......\n天亮了\n昨晚")
            for i in deadtonight:
              if ML[i-1]['job']=='WL':
                wf-=1
              await ch.send(ML[i-1]['name'])
              ML[i-1]['job']="DE"
              me-=1
            await ch.send("被殺了")
            if wf==0:
              await ch.send("人類勝利")
              reset()
            elif me-wf<=wf:
              await ch.send("狼人勝利")
              reset()
            else:
              await ch.send("遊戲尚未結束請使用 #vote (玩家編號) 來投票")
              await ch.send(name)
              mode=7
      else:
        await ctx.send("你已經用過了")
    else:
      await ctx.send("阿就不是女巫在那邊搞")
  else:
    await ctx.send("遊戲階段錯誤")

@bot.command()
async def topass(ctx):
  global WI,mode,DR,me,name,healthused,hunterdead,deadtonight,jobarr,wf
  if mode==3:
    if check(ctx.author,"WI"):
      if me>9:
        await ch.send("女巫請閉眼......\n預言家現身請睜眼")
        await jobarr[1][0].send("請使用 #examine (玩家編號)來查驗身分")
        await jobarr[1][0].send(name)
        mode=5
      else:
        for i in deadtonight:
          if ML[i-1]["job"] =="HU":
            await ch.send("女巫請閉眼......\n獵人現身請睜眼")
            await jobarr[2][0].send("你死了 請使用#bring (玩家編號)來選擇要帶走的人")
            await jobarr[2][0].send(name)
            mode=6
            hunterdead=1
        if hunterdead==0:
          await ch.send("獵人請睜眼\n獵人請閉眼......\n天亮了\n昨晚")
          for i in deadtonight:
            if ML[i-1]['job']=='WL':
              wf-=1
            await ch.send(ML[i-1]['name'])
            ML[i-1]['job']="DE"
            me-=1
          await ch.send("被殺了")
          if wf==0:
            await ch.send("人類勝利")
            reset()
          elif me-wf<=wf:
            await ch.send("狼人勝利")
            reset()
          else:
            await ch.send("遊戲尚未結束請使用 #vote (玩家編號) 來投票")
            await ch.send(name)
            mode=7
    else:
      await ctx.send("阿就不是女巫在那邊搞")
  else:
    await ctx.send("遊戲階段錯誤")
  
#----------------------------------------------------------------------------------------------------------#
@bot.command()
async def examine(ctx,input:int):
  global mode,hunterdead,name,deadtonight,ch,me,ML
  if mode==5:
    if ctx.author == jobarr[1][0]:
      if ML[input-1]['job']=="WL":
        await ctx.send("他是狼人")
      else:
        await ctx.send("他是好人")
      for i in deadtonight:
        if ML[i-1]["job"] =="HU":
          await ch.send("女巫請閉眼......\n獵人現身請睜眼")
          await jobarr[2][0].send("你死了 請使用#bring (玩家編號)來選擇要帶走的人")
          await jobarr[2][0].send(name)
          mode=6
          hunterdead=1
      if hunterdead==0:
        await ch.send("獵人請睜眼\n獵人請閉眼......天亮了\n昨晚")
        for i in deadtonight:
          await ch.send(ML[i-1]['name'])
          ML[deadtonight-1]['job']="DE"
          me-=1
        await ch.send("被殺了")
        if wf==0:
          await ch.send("人類勝利")
          reset()
        elif me-wf<=wf:
          await ch.send("狼人勝利")
          reset()
        else:
          await ch.send("遊戲尚未結束\n請使用#vote來投票")
          mode=7
    else:
      await ctx.send("阿就不是預言家在那邊搞")
  else:
    await ctx.send("遊戲階段錯誤")
#----------------------------------------------------------------------------------------------------------#
@bot.command()
async def bring(ctx,input:int):
  global mode,deadtonight,ch,hunterout,wf,me
  if mode ==6:
    if check(ctx.author,"HU"):
      if hunterout==1:
        await ch.send(f"{input}號被獵人帶走了")
        ML[input-1]['job']='DE'
        if ML[input-1]['job']=='WL':
          wf-=1
        me-=1
        namegenerate()
        if wf==0:
          await ch.send("人類勝利")
          reset()
        elif me<=wf-me:
          await ch.send("狼人勝利")
          reset()
        else:
          await ch.send("天黑請閉眼\n狼人現身請睜眼")
          for i in jobarr[0]:
            await i.send('\n請選擇要殺的對象  回復:#kill (玩家編號)')
            await i.send(nameforwolf)
          mode=2
      else:
        await ch.send("獵人請閉眼......天亮了\n昨晚")
        for i in deadtonight:
          if ML[i-1]['job']=='WL':
            wf-=1
          await ch.send(ML[i-1]['name'])
          ML[i-1]['job']="DE"
          me-=1
        await ch.send("被殺了")
        await ch.send(f"且{ML[input-1]['name']}被獵人帶走了")
        namegenerate()
        if wf==0:
          await ch.send("人類勝利")
          reset()
        elif me-wf<=wf:
          await ch.send("狼人勝利")
          reset()
        else:
          await ch.send("請使用 #vote (玩家編號) 來投票")
          await ch.send(name)
          mode=7
    else:
      await ctx.send ("阿就不是獵人在那邊搞")
  else:
    await ctx.send("遊戲階段錯誤")
#----------------------------------------------------------------------------------------------------------#
@bot.command()
async def vote(ctx,input:int):
  global name,mode,ch,me,votetoout,hunterdead,hunterout,deadtonight,wf
  if mode==7:
    if check(ctx.author,"DE"):
      await ctx.send("阿你就死了齁")
    else:
      votetoout.append(input)
      if len(votetokill) == me:
        votetoout.sort()
        if votetoout[0]==votetoout[1]:
          await ctx.send("最高票重複\n請重投")
        else:
          await ctx.send(f"{ML[max(votetoout,key=votetoout.count)-1]['name']}出局")
          if ML[max(votetoout,key=votetoout.count)-1]['job']=='HU':
            await ch.send("獵人發動技能")
            await jobarr[2][0].send("你死了 請使用#bring (玩家編號)來選擇要帶走的人")
            await jobarr[2][0].send(name)
            mode=6
            hunterdead=1
            hunterout=1
          else:
            ML[max(votetoout,key=votetoout.count)-1]['job']="DE"
            me-=1
            votetoout = []
            if wf==0:
              await ch.send("人類勝利")
              reset()
            elif me-wf<=wf:
              await ch.send("狼人勝利")
              reset()
            else:
              await ch.send("天黑請閉眼......\n狼人現身請睜眼")
              for i in jobarr[0]:
                  await i.send('\n請選擇要殺的對象  回復:#kill (玩家編號)')
                  await i.send(nameforwolf)
              mode=2
  else:
    await ctx.send("還沒投票拉不要耍肛")
#----------------------------------------------------------------------------------------------------------#
@bot.command()
async def start(ctx):
    global mode,me,ML,ch
    ch = ctx.channel
    if mode==0:
        reset()
        await ctx.send('請輸入"#join"來加入這場遊戲(支援6~11人)\n都打好後輸入"#go"來開啟遊戲')
        mode=1
    else:
        await ctx.send('您的遊戲尚未洗白請洗白後再試')
@bot.command()
async def end(ctx):
  global mode
  if mode==0:
    await ctx.send("還沒開始就結束了,像極了愛情")
  else:
    reset()
    await ch.send("遊戲已洗白")
#----------------------------------------------------------------------------------------------------------#
@bot.command()
async def join(ctx):
  global mode,me,ML,ch
  if(mode==1):
    if(me==11):
      await ch.send("人數已達上限")
    else :
      if ctx.author in namenumdic.keys():
        await ch.send("無法重複加入")
      else:
        me+=1
        ML.append({"num":me,
                   "name":ctx.author,
                   "job":""})
        namenumdic[ctx.author]=me
        print (f"{ctx.author} join ({me})")
        await ch.send(f"<@!{ctx.author.id}> 成功加入 已有{me}人") 
  else:
      await ch.send("遊戲階段錯誤")
@bot.command()
async def leave(ctx):
    global mode,me,ML,ch,namenumdic
    if mode ==1:
      if ctx.author in namenumdic.keys():
        del ML[namenumdic[ctx.author]-1]
        del namenumdic[ctx.author]
        print (ctx.author,"leave")
        await ch.send(f"<@!{ctx.author.id}> 已離開 剩餘{me-1}人")
        me-=1
      else:
        await ch.send("阿你就不在裡面齁")
    else:
      await ch.send("遊戲階段錯誤")
#----------------------------------------------------------------------------------------------------------#

keepalive.keep_alive()
bot.run('token')