import geopy.geocoders
import tkinter as tk
from tkinter import messagebox, END
from geopy import distance
from geopy.geocoders import Nominatim
import json
from urllib.request import urlopen
from youtube_search import YoutubeSearch as yt 
import wikipedia as wk
import folium
from folium.plugins import MeasureControl
import webbrowser

class Woe:
    def __init__(self, key_city, lat, lon):
        self.key_city = key_city
        self.lat = lat
        self.lon = lon
    
    def myLocation(self):  #내 위치 
        response = urlopen("http://ip-api.com/json").read()
        responseJson = json.loads(response)
        rJ = responseJson
        return rJ.get("city")
    
    def locInfo(self, key): #입력한 도시 정보
        geopy.geocoders.options.default_timeout = 10
        geolocator = Nominatim(user_agent="hoon")
        try: 
            location = geolocator.geocode(key, language = 'en')
            address_key_loc = location.address #(도착지) 주소
            latitude_key_loc = location.latitude #위도
            longitude_key_loc = location.longitude #경도
        except: return False
        else: 
            new_address_key_loc = address_key_loc.replace('-si', '')
            return new_address_key_loc, latitude_key_loc, longitude_key_loc

    def wikiSumm(self, wk_key_word):
        wk.set_lang('en')
        try: 
            summ = wk.summary(wk_key_word, sentences = 3)
            page_name = wk_key_word
        except wk.exceptions.DisambiguationError:
            beatAmbig = wk.search(wk_key_word) #disambig파일에서 첫번째는 자신 파일이고 두 번째 부터가 세부 파일
            summ = wk.summary(beatAmbig[1], sentences = 3)
            page_name = beatAmbig[1]
        except wk.exceptions.PageError:
            summ = 'CANNOT FIND ANY DATA'
            page_name = ''
        finally:
            summ_html = '<p><strong>%s</strong><br>%s..</p>' % ('◈Wiki summary of '+wk_key_word+'◈', summ)
            #위키 원본 사이트 주소 만들기
            wikipg = page_name.replace(' ', '_')
            wiki_origin_html = '<a href="https://en.wikipedia.org/wiki/%s">more</a>' % wikipg 
            return summ_html, wiki_origin_html, page_name

    def wikiImage(self, pg_name): #위키 문서 이미지 추출 (2번째)
        pg = wk.page(pg_name)
        img = pg.images[1:2]
        img_html_h = '<img style="width: 256px;" src=%s alt= %s align="left" hspace = "10" vspace = "5">' % (img[0], self.key_city)
        img_html_t = '</img>'
        return img_html_h, img_html_t
    
    def wikiGeo(self): #주변 장소
        related = wk.geosearch(self.lat, self.lon, results = 5, radius = 7000)
        return related
    
    def youtubeSearch(self, sfx_cmd):#suffix, 유튜브 영상 찾고 원본 주소, iframe 플레이어 html코드 제작
        if sfx_cmd == 1: sfx = ' vlog'
        elif sfx_cmd == 2: sfx = ' downtown driving'
        else: sfx = ''
        key_word = self.key_city+sfx
        adp_key = key_word.replace(' ', '+')
        results = yt(key_word, max_results=1).to_dict()
        try:
            vid = results[0]['id']
        except: Back_n_Forth(0,0,0).errorBox()    

        vid_html = '<iframe width="595" height="350" src="https://www.youtube.com/embed/'+vid+'" frameborder="5" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'
        yt_origin_html = '<br><a href="https://www.youtube.com/results?search_query=%s">More videos</a>' % adp_key
        return vid_html, yt_origin_html

    def theMap(self, main_html, rel_html, rel_pts_names):
        tool_tip = 'Show pannel'
        #목적지 점 찍고 html 만들기
        main_pt = [self.lat, self.lon]
        m = folium.Map(location=main_pt, zoom_start = 11)
        board = folium.map.Popup(html = main_html,\
                                 parse_html = False,\
                                 max_width = '200%')
        folium.Marker(main_pt, popup= board, tooltip= tool_tip, icon=folium.Icon(color='green',icon='star')).add_to(m)
        # 주변 장소 팝업 만들기
        geo_popUPs = []
        for geo_summs in rel_html:
            geo_htm = geo_summs[0]+geo_summs[1]
            geo_popUPs.append(folium.map.Popup(html = geo_htm,\
                                 parse_html = False,\
                                 max_width = 350))
        # 주변 장소 점 찍기
        index = 0
        for geo_results in rel_pts_names:#{'이름': (위도, 경도), '이름':(위도, 경도), ...} 이런 형태
            folium.Marker(rel_pts_names[geo_results], popup= geo_popUPs[index], tooltip= tool_tip).add_to(m)
            index += 1

        m.add_child(MeasureControl(primary_length_unit='kilometers', primary_area_unit='sqkilometers'))
        m.save('%s.html'%self.key_city)
        webbrowser.open_new_tab('%s.html' % self.key_city)

class Back_n_Forth(Woe):
    def errorBox(self):
        tk.messagebox.showerror('CANNOT TAKE OFF', 'NO DATA:check your word(s) again')

    def programInfo(self):
        app_info = '''Type your destination and select the search option and click the button.

방구석 세계여행 v. 2.0 beta
This program is made by Yeonghun Lim.
March, 2020
'''
        tk.messagebox.showinfo('INFORMATION', app_info)

    def htmlMaker(self, htmls):
        # soup_htmls = [(img_html_h, img_html_t), [summ_html, wiki_origin_html], (vid_html, yt_origin_html)]
        pre_comHTML = htmls[0][0]+htmls[1][0]+htmls[1][1]+htmls[0][1]+htmls[2][0]+htmls[2][1]
        return pre_comHTML

    def struct(self):
        global suf_id, destination
        desti = destination.get()
        usr = Back_n_Forth(desti, 0, 0)
        city_info = usr.locInfo(desti)
        if city_info == False: usr.errorBox()
        else:
            #정확한 도시 이름 추출
            splited_address = city_info[0].split(',')
            city_name = splited_address[0]
            #정확한 도시 이름으로 Woe/Back_n_Forth에 다시 삽입
            usr = Back_n_Forth(city_name, city_info[1], city_info[2])
            wiki_sum_html = usr.wikiSumm(city_name) # 0: summ_html, 1: wiki_origin_html, (2: page_name) -> 다다음 행에서 사라짐
            wiki_sum_html = list(wiki_sum_html)
            wiki_img_html = usr.wikiImage(wiki_sum_html.pop()) # (img_html_h, img_html_t)
            wiki_geo_results = usr.wikiGeo() # ([0:4]까지) 위키 문서 제목
            wiki_geoRel_htmls = []
            wiki_geoRel_info = {}
            for word in wiki_geo_results:
                geoR_html = usr.wikiSumm(word)
                geoR_loc_info = usr.locInfo(word)
                if geoR_loc_info == False: continue
                elif city_info[1] == geoR_loc_info[1]: continue
                else:
                    tmep_htmls = []
                    geoR_loc_info = list(geoR_loc_info)
                    geoR_loc_info.pop(0)
                    wiki_geoRel_info[word] = geoR_loc_info #{'이름': (위도, 경도), '이름':(위도, 경도), ...} 이런 형태
                    tmep_htmls.append(geoR_html[0])
                    tmep_htmls.append(geoR_html[1]) # ([0:4]까지) 각각의 summ_html (e.g.)->[summ_html, wiki_origin_html, summ_html, ...]
                    wiki_geoRel_htmls.append(tmep_htmls)
            yt_vid_html = usr.youtubeSearch(suf_id) # (vid_html, yt_origin_html)

            soup_htmls = []
            soup_htmls.append(wiki_img_html)
            soup_htmls.append(wiki_sum_html)
            soup_htmls.append(yt_vid_html)
            # soup_htmls = [(img_html_h, img_html_t), [summ_html, wiki_origin_html], (vid_html, yt_origin_html)]
            comHTML = usr.htmlMaker(soup_htmls)
            usr.theMap(comHTML, wiki_geoRel_htmls, wiki_geoRel_info)

    def insertMyLoc(self):
        global destination
        destination.delete(0, 50)
        my_city_name = Back_n_Forth(0, 0, 0).myLocation()
        destination.insert(0, my_city_name)
        
    def mainWindow(self): #GUI Window 담당
        global destination, suf_id, pre
        def search_option():
            global suf_id
            suf_id = search_option_radio.get()
            print(suf_id) # 안 하면 자꾸 노란불 생김
        #창 기본 설정
        main = tk.Tk()
        main.title('방구석 세계여행')
        main.geometry('320x180+800+100')
        main.resizable(False, False)
        #help 메뉴
        help_ = tk.Button(main, text='Help', relief='groove', activebackground = 'gray')
        help_.config(command = pre.programInfo)
        #상단 라벨
        label = tk.Label(main, text='Wherever you want...', font = ('', 16))
        #도시 입력 엔트리
        destination = tk.Entry(main, width = 26)
        #내 위치 찾기 버튼
        btn_myLoc = tk.Button(main, text = 'My Location', width = '12', height = '1')
        btn_myLoc.config(command = pre.insertMyLoc)
        #검색 옵션 라디오버튼
        search_option_radio = tk.IntVar()
        vlog_rd = tk.Radiobutton(main, text="Vlog", value=1, variable=search_option_radio)
        vlog_rd.config(command = search_option)
        driv_rd = tk.Radiobutton(main, text="Driving", value=2, variable=search_option_radio)
        driv_rd.config(command = search_option)
        driv_rd.flash()
        none_rd = tk.Radiobutton(main, text="None (not recommended)", value=3, variable=search_option_radio)
        none_rd.config(command = search_option)
        #이륙 버튼 (시작)
        btn_takeOff = tk.Button(main, text = 'TAKE OFF',width = '25', height = '3', bg = 'lightblue',\
                                      activebackground = 'lightblue')
        btn_takeOff.config(command = pre.struct)
        #본격적인 배치
        label.place(x=160, y=10, anchor = 'n')
        destination.place(x=200, y=60, anchor = 'e' )
        btn_myLoc.place(x=215, y=60, anchor = 'w')
        vlog_rd.place(x=10, y=90, anchor = 'w')
        driv_rd.place(x=80, y=90, anchor = 'w')
        none_rd.place(x=150, y=90, anchor = 'w')
        btn_takeOff.place(x=160, y=108, anchor = 'n')
        help_.place(x=2, y=180, anchor = 'sw')

        main.mainloop()

#본격적인 실행
pre = Back_n_Forth(0, 0, 0)
pre.mainWindow()