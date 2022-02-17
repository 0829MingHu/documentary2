
from unittest import result
import requests
import os
import copy
import json
from urllib.parse import urlencode
from typing import List, Union
from constants import *
import time


class ChannelSearch():
    response = None
    responseSource = None
    resultComponents = []

    def __init__(self, query: str, browseId: str, language: str = 'en', region: str = 'US', searchPreferences: str = "EgZzZWFyY2g%3D", timeout: int = 5):
        super().__init__()
        self.query = query
        self.language = language
        self.region = region
        self.browseId = browseId
        self.searchPreferences = searchPreferences
        self.continuationKey = None
        self.url = None
        self.data = None
        self.timeout = timeout
        self.breakpoint = False
        self.proxy = {}
        http_proxy = os.environ.get("HTTP_PROXY")
        if http_proxy:
            self.proxy["http"] = http_proxy
        https_proxy = os.environ.get("HTTPS_PROXY")
        if https_proxy:
            self.proxy["https"] = https_proxy

    def syncPostRequest(self):
        return requests.post(
            self.url,
            headers={"User-Agent": userAgent},
            json=self.data,
            timeout=self.timeout,
            proxies=self.proxy
        )
    
    def _getChannelSearchComponent(self, elements: list) -> list:
        channelsearch = []
        for element in elements:
            if element.get('continuationItemRenderer'):
                new_continuationKey = self._getValue(element, ["continuationItemRenderer", "continuationEndpoint", "continuationCommand", "token"])
                if new_continuationKey==self.continuationKey:
                    self.breakpoint=True
                continue
            responsetype = None
            try:
                element = element["itemSectionRenderer"]["contents"][0]["videoRenderer"]
                responsetype = "video"
            except:
                pass
            
            if responsetype == "video":
                json = {
                    "id":        self._getValue(element, ["videoId"]),
                    "title":     self._getValue(element, ["title", "runs", 0, "text"]),
                    "description":self._getValue(element, ["descriptionSnippet", "runs", 0, "text"]),
                    "duration":  self._getValue(element, ["lengthText", "simpleText"]),
                    "published": self._getValue(element, ["publishedTimeText", "simpleText"]),
                    "channel":   self._getValue(element, ["ownerText", "runs", 0, "text"]),
                    "url":       'https://www.youtube.com'+self._getValue(element, ["navigationEndpoint", "commandMetadata", "webCommandMetadata", "url"]),
                    "type":      responsetype
                }
                channelsearch.append(json)
        return channelsearch


    def _getValue(self, source: dict, path: List[str]) -> Union[str, int, dict, None]:
        value = source
        for key in path:
            if type(key) is str:
                if key in value.keys():
                    value = value[key]
                else:
                    value = None
                    break
            elif type(key) is int:
                if len(value) != 0:
                    value = value[key]
                else:
                    value = None
                    break
        return value

    def next(self):
        if self.breakpoint:
            self.breakpoint=False
            return True
        self._syncRequest()
        self._parseChannelSearchSource()
        self.response = self._getChannelSearchComponent(self.response)
        return self.response

    def _parseChannelSearchSource(self) -> None:
        try:
            if self.response.get('contents'):
                self.response = self.response["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][-1]["expandableTabRenderer"]["content"]["sectionListRenderer"]["contents"]
            elif self.response.get('onResponseReceivedActions'):
                self.response = self.response["onResponseReceivedActions"][0]["appendContinuationItemsAction"]['continuationItems']
        except Exception as e:
            print(e)
            raise Exception('ERROR: Could not parse YouTube response.')

    def _getRequestBody(self):
        requestBody = copy.deepcopy(requestPayload)
        requestBody['query'] = self.query
        requestBody['client'] = {
            'hl': self.language,
            'gl': self.region,
        }
        requestBody['params'] = self.searchPreferences
        requestBody['browseId'] = self.browseId
        if self.continuationKey:
            requestBody['continuation']=self.continuationKey
        # print(requestBody)
        self.url = 'https://www.youtube.com/youtubei/v1/browse' + '?' + urlencode({
            'key': searchKey,
        })
        self.data = requestBody

    def _syncRequest(self) -> None:
        self._getRequestBody()

        request = self.syncPostRequest()
        try:
            self.response = request.json()
            # print(self.response)
        except:
            raise Exception('ERROR: Could not make request.')

    def result(self, mode: int = ResultMode.dict) -> Union[str, dict]:
        '''Returns the search result.

        Args:
            mode (int, optional): Sets the type of result. Defaults to ResultMode.dict.

        Returns:
            Union[str, dict]: Returns JSON or dictionary.
        '''
        if mode == ResultMode.json:
            return json.dumps({'result': self.response}, indent=4)
        elif mode == ResultMode.dict:
            return {'result': self.response}


def main():
    #设置代理
    proxy = 'socks5://127.0.0.1:10808'
    os.environ['HTTP_PROXY']=proxy
    os.environ['HTTPS_PROXY']=proxy

    s=ChannelSearch('monkey','UC-Uh0-0dEQV8a-SPrx50zmw')
    while True:
        flag=s.next()
        result=s.result(mode = ResultMode.dict)
        print(result)
        if flag==True or s.continuationKey==None:
            break
        time.sleep(5)

if __name__=='__main__':
    main()