import os
import sys
import logging

from helper.SeleniumHelper import SeleniumHelper
from selenium import webdriver
from datetime import datetime
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from model.PostModel import PostModel
from pyvirtualdisplay import Display

class PostController(SeleniumHelper):

	# CONFIG
	START_PAGE = 1
	TIMEOUT = 30
	containerElement = None

	def getRequest(self, url, selector):
		for x in range(0, 3):
			print('')
			self.logging('Request %s %d times...' % (url, x + 1))

			# wait show element
			self.containerElement = self.loadAndWait(url + '?times=%s' % (str(x+1)), selector)
			if self.containerElement is not None:
				self.logging('Request is Done!')
				break

	# get list post
	def crawlPosts(self):
		self.logging('Starting...')

		# starting get datas
		while True:
			# refresh page
			if self.containerElement is None:
				self.getRequest('https://ymeet.me/blog/page/%s/' % (self.START_PAGE), '.blog-posts-list')

			# build datas
			created_at = self.getCurrentTime()
			updated_at = created_at
			posts_object = self.driver.execute_script("""
				var posts = [];

				// get all post elements
				var blog_posts_list = jQuery(".blog-posts-list .blog-post");

				// for each post and find data
				jQuery.each(blog_posts_list, function(index, post_element) {
					let post_object = jQuery(post_element);
					let origin_id = post_object.find('article').attr('id').trim();
					let href = post_object.find('.blog-post-thumb > a').attr('href').trim();
					let thumb = post_object.find('img.wp-post-image').attr('src').trim();
					let title = post_object.find('h2.entry-title > a').text().trim();
					let description = post_object.find('.entry-content > p').text().trim();

					posts.push({
						origin_id: origin_id.split('-')[1],
						origin_url: href,
						title: title,
						description: description,
						image: thumb,
						crawl_status: description ? 1 : 0,
						created_at: '%(created_at)s',
						updated_at: '%(updated_at)s'
					});
				});

				// reorder
				posts.reverse();

				return {
					status: posts && posts.length > 0 ? true : false,
					data: posts
				};
			""" % {
				'created_at': created_at,
				'updated_at': updated_at
			})

			# insert into database
			if posts_object['status']:
				for data in posts_object['data']:
					if PostModel.save(data) > 0:
						self.logging("inserted successfully!")

			self.containerElement = None

			print('')
			if self.START_PAGE > 1:
				self.START_PAGE -= 1
			else:
				break


	# get list post
	def handlePosts(self):
		self.logging('Starting...\n')

		posts = PostModel.findPostNoContent()

		for post in posts:
			# refresh page
			if self.containerElement is None:
				self.getRequest(post['origin_url'], '.post-container')

			# build datas
			updated_at = self.getCurrentTime()
			post_object = self.driver.execute_script("""
				var content_element = jQuery('.entry-content');
				var description = content_element.text().trim().substr(0, 200) + '...';
				return {
					status: description ? true : false,
					data: {
						description: description,
						crawl_status: description ? 1 : 0,
						updated_at: '%(updated_at)s'
					}
				}
			""" % {
				'updated_at': updated_at
			})

			# insert into database
			if post_object['status']:
				params = post_object['data']

				if post['description'] != '':
					params['description'] = post['description'];

				success = PostModel.updatePost(post['id'], params)
				if success:
					self.logging("Post %d: updated successfully!" % (post['id']))

			self.containerElement = None

		self.driver.close()

	#
	# Log writer
	#
	def logging(self, log):
		currentTimes = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		logs = currentTimes + ': ' + str(log)
		print(logs)

	def getCurrentTime(self):
		return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

	#
	# Init
	#
	def __init__(self, startPage=1):
		# page start for crawler
		self.START_PAGE = startPage
		
		# start display
		display = Display(visible=0, size=(800, 600))
		display.start()
		logging.info('Initialized virtual display..')

		firefox_profile = webdriver.FirefoxProfile()
		firefox_profile.set_preference('browser.download.folderList', 2)
		firefox_profile.set_preference('browser.download.manager.showWhenStarting', False)
		firefox_profile.set_preference('browser.download.dir', os.getcwd())
		firefox_profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')

		logging.info('Prepared firefox profile..')

		self.driver = webdriver.Firefox(firefox_profile=firefox_profile)
		logging.info('Initialized firefox browser..')

		self.driver.set_page_load_timeout(self.TIMEOUT)
