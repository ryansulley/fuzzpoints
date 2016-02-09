import gdb, math, random, struct

class fuzzpoint (gdb.Breakpoint):

  def __init__(self, trigger, target, size, factor):
    self.target = target
    self.size = size
    self.factor = factor
    super(fuzzpoint,self).__init__(trigger)

  def stop(self):
    buf_size = gdb.parse_and_eval(self.size)
    
    mod_count = int(math.floor(buf_size * 8 * gdb.parse_and_eval(self.factor)))
    if mod_count < 1: mod_count = 1
   
    for i in range(0, mod_count):
      offset = random.randint(0,buf_size-1)
      rand_byte = gdb.parse_and_eval('%s + %d' % (self.target, offset))
      buf = gdb.selected_inferior().read_memory(rand_byte, 1)
      orig = struct.unpack('B', buf[0])[0]
      rand_bit = random.randint(0,7)
      update = (orig ^ (1 << rand_bit))
      gdb.selected_inferior().write_memory(rand_byte, chr(update), 1)
    return False
    
    

class fuzz (gdb.Command):
  """Create a fuzzpoint with a given trigger, target, size, factor, and seed"""

  def __init__ (self):
    super (fuzz, self).__init__ ("fuzz", gdb.COMMAND_USER)

  def invoke (self, arg, from_tty):
    argv = gdb.string_to_argv(arg)
    if len(argv) < 5:
      print("Error: requires arguments [trigger] [target] [size] [factor] [seed]")
      return

    seed     = gdb.parse_and_eval(argv[4])
    random.seed(seed) 
    fuzzpoint(argv[0], argv[1], argv[2], argv[3])

fuzz()
