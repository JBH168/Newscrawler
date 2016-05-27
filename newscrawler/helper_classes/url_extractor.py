import re


class url_extractor(object):
    def get_allowed_domains(self, url):
        # not looking out for any leading "www."
        return [re.search('[^/]+\.[^/]+', url).group(0)]

    def get_sitemap_urls(self, url, allow_subdomains=True):
        allowed_domains = self.get_allowed_domains(url)[0]
        if allow_subdomains:
            return ["http://" + allowed_domains + "/robots.txt"]
        else:
            without_subdomain = re.search(
                '[^/.]+\.[^/.]+$', allowed_domains).group(0)
            return ["http://" + without_subdomain + "/robots.txt"]

    def get_start_urls(self, url):
        allowed_domains = self.get_allowed_domains(url)[0]
        return ["http://" + allowed_domains + "/"]
