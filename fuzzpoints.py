import gdb, math, random, struct

class fuzzpoint (gdb.Breakpoint):

  def __init__(self, trigger, target, size, factor):
    self.target = target
    self.size = size
    self.factor = factor
    super(fuzzpoint,self).__init__(trigger)

  def stop(self):
    buf_loc = gdb.parse_and_eval(self.target)
    buf_size = gdb.parse_and_eval(self.size)
    
    mod_count = int(math.floor(buf_size * 8 * gdb.parse_and_eval(self.factor)))
    if mod_count < 1: mod_count = 1

    buf = gdb.selected_inferior().read_memory(buf_loc, buf_size)
    for i in range(0,mod_count):
      rand_byte = random.randint(0,buf_size-1)
      orig = struct.unpack('B', buf[rand_byte])[0]
      rand_bit = random.randint(0,7)
      update = (orig ^ (1 << rand_bit))
      gdb.selected_inferior().write_memory(buf_loc, chr(update), 1)
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

    trigger = argv[0]
    target   = argv[1]
    size     = argv[2] 
    factor   = argv[3]
    seed     = gdb.parse_and_eval(argv[4])
    random.seed(seed) 
    fuzzpoint(trigger, target, size, factor)

fuzz()
