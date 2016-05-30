import re
import os


class url_extractor(object):
    def get_allowed_domains(self, url):
        return re.sub(r'^(www.)', '', re.search('[^/]+\.[^/]+', url).group(0))

    def get_allowed_domains_without_subdomains(self, url):
        return re.search('[^/.]+\.[^/.]+$',
                         self.get_allowed_domains(url)).group(0)

    def get_sitemap_urls(self, url, allow_subdomains):
        if allow_subdomains:
            return "http://" + self.get_allowed_domains(url) + "/robots.txt"
        else:
            return "http://" + \
                    self.get_allowed_domains_without_subdomains(url) + \
                    "/robots.txt"

    def get_start_urls(self, url):
        allowed_domains = self.get_allowed_domains(url)
        return "http://" + allowed_domains + "/"

    def get_url_directory_string(self, url):
        domain = self.get_allowed_domains(url)

        splitted_url = url.split('/')

        # the following commented list comprehension could replace
        # the following for, if not and break statement
        # index = [index for index in range(len(splitted_url))
        #          if not re.search(domain, splitted_url[index]) is None][0]
        for index in range(len(splitted_url)):
            if not re.search(domain, splitted_url[index]) is None:
                if splitted_url[-1] is "":
                    splitted_url = splitted_url[index + 1:-2]
                else:
                    splitted_url = splitted_url[index + 1:-1]
                break

        return '_'.join(splitted_url)

    def get_url_file_name(self, url):
        url_root_ext = os.path.splitext(url)

        # len(".markdown") = 9
        if (len(url_root_ext[1]) < 10):
            return os.path.split(url_root_ext[0])[1]
        else:
            return os.path.split(url)[1]
