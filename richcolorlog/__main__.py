try:
	from . logger import run_test
except Exception as e:
	from logger import run_test

def main():
	run_test()

if __name__ == '__main__':
	run_test()