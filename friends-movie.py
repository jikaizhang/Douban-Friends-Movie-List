from bs4 import BeautifulSoup
import requests
import csv

file = open("friends-movie.txt", "r")
links = file.read().splitlines()
# use Douban's sort by rating
page_str1 = "?start="
# in the middle is a multiple of 15
page_str2 = "?sort=rating&mode=grid&tags_sort=count"
movie_dict = dict()
csv_name = 'Movies_My_Friends_Watch.csv'

def main_loop(soup):
    k = 0
    for li in soup.find_all('div', class_="info"):
        k = k + 1
        # skip the first div, it contains useless info
        if k == 1: continue
        # the key
        movie_link = li.ul.find_all('li')[0].a.get("href")
        movie_title = li.ul.find_all('li')[0].a.em.text.split('/')[0]
        # the value (title, num_view, num_rate, total_star, average_score)
        # average_score will be computed after the loop
        info = [movie_title, 0, 0, 0, 0.0]
        if movie_link not in movie_dict:
            movie_dict[movie_link] = info
        movie_dict[movie_link][1] = movie_dict[movie_link][1] + 1、
        try:
            temp_rating_str = li.ul.find_all('li')[2].find('span').get("class")
        except:
            continue
        # if the user didn't rate, we will get different string
        if temp_rating_str[0][0] == 'r':
            rate_star = int(temp_rating_str[0][6])
            movie_dict[movie_link][2] = movie_dict[movie_link][2] + 1
            movie_dict[movie_link][3] = movie_dict[movie_link][3] + rate_star

for i in range(len(links)):
    source = requests.get(links[i]).text
    soup = BeautifulSoup(source, 'html.parser')
    total_page_num = int(soup.find('div', class_="paginator").find_all('span')[1].get("data-total-page"))
    print("Friend #" + str(i+1) + " (" + str(total_page_num) + " pages)")
    for j in range(total_page_num):
        page_link = links[i] + page_str1 + str(j * 15) + page_str2
        source = requests.get(page_link).text
        soup = BeautifulSoup(source, 'html.parser')
        main_loop(soup)
        if (j + 1) % 10 == 0:
            print("Page: " + str(j+1) + "/" + str(total_page_num))
    print("Number of friends complete: " + str(i+1) + "/" + str(len(links)))

    for link in movie_dict:
        num_rate = movie_dict[link][2]
        total_star = movie_dict[link][3]
        avg = 0.0
        if num_rate != 0:
            avg = float(total_star * 2 / num_rate)
        movie_dict[link][4] = avg
    with open(csv_name, 'w', newline='', encoding='utf-8-sig') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Title", "# Views", "# Rates", "Average Score", "Douban Link"])
        for link, info in movie_dict.items():
            writer.writerow([info[0], info[1], info[2], info[4], link])
    print("Successfully write " + str(i+1) + " friends to csv file")
