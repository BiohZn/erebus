#!/usr/bin/python

#TODO: tons

import os, sys, select, MySQLdb, MySQLdb.cursors
import bot, config

class Erebus(object):
	bots = {}
	fds = {}
	mods = {}
	msghandlers = {}

	class User(object):
		chans = []

		def __init__(self, nick, auth=None):
			self.nick = nick
			self.auth = auth

			if auth is not None:
				self.checklevel()

		def authed(self, auth):
			self.auth = auth
			self.checklevel()

		def checklevel(self): self.level = 9999 #TODO get level from db

		def __str__(self): return self.nick
		def __repr__(self): return "<User %r>" % (self.nick)

	class Channel(object):
		users = []
		voices = []
		ops = []

		def __init__(self, name):
			self.name = name

		def userjoin(self, user, level=None):
			if user not in self.users: self.users.append(user)
			if level == 'op' and user not in self.ops: self.ops.append(user)
			if level == 'voice' and user not in self.voices: self.voices.append(user)
		def userpart(self, user):
			if user in self.ops: self.ops.remove(user)
			if user in self.voices: self.voices.remove(user)
			if user in self.users: self.users.remove(user)

		def userop(self, user):
			if user in self.users and user not in self.ops: self.ops.append(user)
		def uservoice(self, user):
			if user in self.users and user not in self.voices: self.voices.append(user)
		def userdeop(self, user):
			if user in self.ops: self.ops.remove(user)
		def userdevoice(self, user):
			if user in self.voices: self.voices.remove(user)

		def __str__(self): return self.name
		def __repr__(self): return "<Channel %r>" % (self.name)

	def __init__(self):
		if os.name == "posix":
			self.potype = "poll"
			self.po = select.poll()
		else: # f.e. os.name == "nt" (Windows)
			self.potype = "select"
			self.fdlist = []

	def newbot(self, nick, user, bind, server, port, realname, chans):
		if bind is None: bind = ''
		obj = bot.Bot(self, nick, user, bind, server, port, realname, chans)
		self.bots[nick.lower()] = obj

	def newfd(self, obj, fileno):
		self.fds[fileno] = obj
		if self.potype == "poll":
			self.po.register(fileno, select.POLLIN)
		elif self.potype == "select":
			self.fdlist.append(fileno)

	def bot(self, name): #get Bot() by name (nick)
		return self.bots[name.lower()]
	def fd(self, fileno): #get Bot() by fd/fileno
		return self.fds[fileno]

	def user(self, nick): #TODO #get User() by nick
		return self.User(nick.lower())
	def channel(self, name): #TODO #get Channel() by name
		return self.Channel(name.lower())

	def poll(self):
		if self.potype == "poll":
			return [fd for (fd, ev) in self.po.poll()]
		elif self.potype == "select":
			return select.select(self.fdlist, [], [])[0]

	def connectall(self):
		for bot in self.bots.itervalues():
			if bot.conn.state == 0:
				bot.connect()

	#module functions
	def modlist(self): pass
	def hasmod(self, name): pass
	def loadmod(self, name): pass
	def unloadmod(self, name): pass
	def reloadmod(self, name): pass

	#bind functions
	def bind(self, word, handler): pass
	def addbind(self, word, handler): pass
	def rmbind(self, word, handler): pass
	def getbind(self, word, handler): pass

cfg = config.Config('bot.config')
main = Erebus()

def setup():
	main.db = MySQLdb.connect(host=cfg.dbhost, user=cfg.dbuser, passwd=cfg.dbpass, db=cfg.dbname, cursorclass=MySQLdb.cursors.DictCursor)
	c = main.db.cursor()
	c.execute("SELECT nick, user, bind FROM bots WHERE active = 1")
	rows = c.fetchall()
	c.close()
	for row in rows:
		c2 = main.db.cursor()
		c2.execute("SELECT chname FROM chans WHERE bot = %s AND active = 1", (row['nick'],))
		chans = [chdic['chname'] for chdic in c2.fetchall()]
		c2.close()
		main.newbot(row['nick'], row['user'], row['bind'], cfg.host, cfg.port, cfg.realname, chans)
	main.connectall()

def loop():
	poready = main.poll()
	for fileno in poready:
		main.fd(fileno).getdata()

if __name__ == '__main__':
	setup()
	while True: loop()
