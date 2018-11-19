def pdec(dec):
   def p_decorate(func):
      def func_wrapper(name):
         return "{0} {1} {0}".format(dec, func(name))
      
      return func_wrapper
   return p_decorate

@pdec("foo")
def get_text(name):
   return "lorem ipsum, {0} dolor sit amet".format(name)

print(get_text("John"))

