class Pizza:
    def __init__(self, ingredients):
        self.ingredients = ingredients

    def __repr__(self):
        return f'Pizza({self.ingredients!r})'

    @classmethod
    def margherita(cls):
        return cls(['mozzarella', 'tomatoes'])

    @classmethod
    def prosciutto(cls):
        return cls(['mozzarella', 'tomatoes', 'ham'])


my_cls = Pizza.margherita()

print(f'{my_cls}')
my_cls = my_cls.prosciutto()
print(f'{my_cls}')
print(f"bibi")
