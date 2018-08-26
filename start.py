import sys
import os
import time
import getopt
from controller.PostController import PostController

def main(params):
	startPage = 1

	opts, args = getopt.getopt(params, "p:")
	if opts:
		for o, a in opts:
			if o == "-p":
				startPage = int(a)
				
	postObject = PostController(startPage)
	postObject.crawlPosts()
	postObject.handlePosts()

if __name__ == "__main__":
    argv = sys.argv[1:]
    main(argv)
