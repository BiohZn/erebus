import ConfigParser

class Config(object):
#	config = ConfigParser.SafeConfigParser()
	def __init__(self, filename, writeout=True):
		self.__dict__['config'] = ConfigParser.SafeConfigParser()
		self.__dict__['filename'] = filename
		self.__dict__['writeout'] = writeout
		self.config.read(filename)

	def __getattr__(self, key):
		return self.config.get('erebus', key)

	def __setattr__(self, key, value):
		self.config.set('erebus', key, value)

	def items(self):
		return self.config.items('erebus')

	def write(self):
		with open(self._filename, 'wb') as configfile:
			self.config.write(configfile)

	def __del__(self):
		if self.writeout: self.write()


if __name__ == '__main__':
	import sys
	cfg = Config(sys.argv[1], False)

	for k, v in cfg.items():
		print k, '=', v
