try:
	from . logger import test
except Exception as e:
	from logger import test

def main():
	test()

if __name__ == '__main__':
	test()