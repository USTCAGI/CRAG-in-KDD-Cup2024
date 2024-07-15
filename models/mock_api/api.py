from models.mock_api.tools.financetools import FinanceTools
from models.mock_api.tools.musictools import MusicTools
from models.mock_api.tools.movietools import MovieTools
from models.mock_api.tools.sportstools import SportsTools
from models.mock_api.tools.generaltools import find_date_from_text, find_date_from_text_all, extract_date, extract_date_, get_last_week_dates, get_last_month_dates, get_this_week_dates, get_this_month_dates
from models.mock_api.prompts import NER_MOVIE_SYSTEM_PROMPT, NER_MOVIE_USER_PROMPT, NER_MUSIC_SYSTEM_PROMPT, NER_MUSIC_USER_PROMPT, NER_SPORTS_SYSTEM_PROMPT, NER_SPORTS_USER_PROMPT, NER_FINANCE_SYSTEM_PROMPT, NER_FINANCE_USER_PROMPT, NER_OPEN_SYSTEM_PROMPT, NER_OPEN_USER_PROMPT
import re
from collections import defaultdict
import datetime
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser

class MockAPI:
    def __init__(self, chat_model):
        self.finance_tool = FinanceTools()
        self.music_tool = MusicTools()
        self.movie_tool = MovieTools()
        self.sports_tool = SportsTools()
        self.ner_chain = self.format_ner_prompt | chat_model | StrOutputParser()

    def format_ner_prompt(self, input):
        query = input['query']
        domain = input['domain']
        if domain == "movie":
            message = [
                SystemMessage(NER_MOVIE_SYSTEM_PROMPT),
                HumanMessage(NER_MOVIE_USER_PROMPT.format(query=query))
            ]
        elif domain == "finance":
            message = [
                SystemMessage(NER_FINANCE_SYSTEM_PROMPT),
                HumanMessage(NER_FINANCE_USER_PROMPT.format(query=query))
            ]
        elif domain == "music":
            message = [
                SystemMessage(NER_MUSIC_SYSTEM_PROMPT),
                HumanMessage(NER_MUSIC_USER_PROMPT.format(query=query))
            ]
        elif domain == "sports":
            message = [
                SystemMessage(NER_SPORTS_SYSTEM_PROMPT),
                HumanMessage(NER_SPORTS_USER_PROMPT.format(query=query))
            ]
        else:
            message = [
                SystemMessage(NER_OPEN_SYSTEM_PROMPT),
                HumanMessage(NER_OPEN_USER_PROMPT.format(query=query))
            ]
        return message
            
    
    def ner_output_parser(self, output, domain):
        results = defaultdict(set)
        if domain == "movie":
            pattern = re.compile(r'^(.*?)(\((person|movie)\))', re.MULTILINE)
            matches = pattern.finditer(output)
            keys = ['person', 'movie']
        if domain == "finance":
            pattern = re.compile(r'^(.*?)(\((company|symbol)\))', re.MULTILINE)
            matches = pattern.finditer(output)
            keys = ['company', 'symbol']
        if domain == "music":
            pattern = re.compile(r'^(.*?)(\((person|song|band)\))', re.MULTILINE)
            matches = pattern.finditer(output)
            keys = ['person', 'song', 'band']
        if domain == "sports":
            pattern = re.compile(r'^(.*?)(\((nba team|soccer team|nba player|soccer player)\))', re.MULTILINE)
            matches = pattern.finditer(output)
            keys = ['nba team', 'soccer team', 'nba player', 'soccer player']
        if domain == "open":
            pattern = re.compile(r'^(.*?)(\((person|location|orgnization|product|event)\))', re.MULTILINE)
            matches = pattern.finditer(output)
            keys = ['person', 'location', 'orgnization', 'product', 'event']

        for match in matches:
            text = match.group(1).strip()
            # 删除所有非字母字符开头的部分
            text = re.sub(r'^[^a-zA-Z]+', '', text)
            if 'none' in text.lower():
                continue
            if match.group(3) in keys:
                results[match.group(3)].add(text)
        
        for key in keys:
            results[key] = list(results[key])
        return results
        

    def ner(self, queries, domains):
        inputs = [{'query': query, 'domain': domain} for query, domain in zip(queries, domains)]
        responses = self.ner_chain.batch(inputs)
        results = []
        for i, response in enumerate(responses):
            results.append(self.ner_output_parser(response, domains[i]))
        return results 
    
    def name_entity_match(self, ner_result, domain):
        matched_entities = defaultdict(list)
        if domain == "finance":
            for name in ner_result['company']:
                if name.strip().lower() in self.finance_tool.name2symbol:
                    matched_entities['symbol'].append(self.finance_tool.name2symbol[name.strip().lower()])
                elif name.upper() in self.finance_tool.all_symbols:
                    matched_entities['symbol'].append(name.upper())
                else:
                    company_name = self.finance_tool.get_company_name(name)
                    if company_name is not None and len(company_name) > 0:
                        matched_entities['symbol'].append(self.finance_tool.name2symbol[company_name[0].strip().lower()])
            for symbol in ner_result['symbol']:
                if symbol.upper() in self.finance_tool.all_symbols:
                    matched_entities['symbol'].append(symbol.upper())
        if domain == "music":
            for name in ner_result['person']:
                if self.music_tool.get_artist_name(name) is not None:
                    matched_entities['person'].append(self.music_tool.get_artist_name(name))
            for name in ner_result['song']:
                if self.music_tool.get_song_name(name) is not None:
                    matched_entities['song'].append(self.music_tool.get_song_name(name))
            for name in ner_result['band']:
                matched_entities['band'].append(name)
        if domain == "movie":
            for name in ner_result['movie']:
                matched_entities['movie'] += self.movie_tool.get_movie_id(name)
            for name in ner_result['person']:
                matched_entities['person'] += self.movie_tool.get_person_id(name)
        if domain == "sports":
            for name in ner_result['nba team']:
                if name in self.sports_tool.nba_teams:
                    matched_entities['nba team'].append(name)
            for name in ner_result['soccer team']:
                if name in self.sports_tool.soccer_teams:
                    matched_entities['soccer team'].append(name)
            for name in ner_result['nba player']:
                matched_entities['nba player'].append(name)
            for name in ner_result['soccer player']:
                matched_entities['soccer player'].append(name)
        return matched_entities
        
    def get_date_info(self, query, query_time):
        date, date_str = find_date_from_text(query_time, query)
        if date_str is not None:
            return f"{date_str} of {query_time[6:10] + '-' + query_time[0:2] + '-' + query_time[3:5]} is {date}"
        return None
    
    def get_movie_info(self, query, query_time, matched_entities):
        movie_ids = matched_entities['movie']
        person_ids = matched_entities['person']
        info = ""
        for movie_id in movie_ids:
            movie_info = self.movie_tool.get_movie_info_by_id(movie_id)
            info += f"#### Some information of {movie_info['title']}\n"
            info += f"- Original Title: {movie_info['original_title']}\n"
            info += f"- Release Date: {movie_info['release_date']}\n"
            if "crew" in movie_info:
                crew = movie_info['crew']
                directors = [person['name'] for person in crew if person['job'] == 'Director']
                if len(directors) > 0:
                    info += f"- Director(s): {', '.join(directors)}\n"
            genres = movie_info['genres']
            if len(genres) > 0:
                genres = [genre['name'] for genre in genres]
                info += f"- Genres: {', '.join(genres)}\n"
            info += f"- Original Language: {movie_info['original_language']}\n"
            if "revenue" in movie_info:
                if movie_info['revenue'] == 0:
                    info += "- Revenue: Unknown\n"
                else:
                    info += f"- Revenue: {movie_info['revenue']}\n"
            if "budget" in movie_info:
                if movie_info['budget'] == 0:
                    info += "- Budget: Unknown\n"
                else:
                    info += f"- Budget: {movie_info['budget']}\n"
            if "length" in movie_info:
                info += f"- Length: {movie_info['length']} minutes\n"
            if "oscar_awards" in movie_info:
                oscar_awards = movie_info['oscar_awards']
                if len(oscar_awards) > 0:
                    info += f"- Oscar Awards:\n"
                    for award in oscar_awards:
                        info += f"    - Category: {award['category']}\n"
                        info += f"        - Year: {award['year_ceremony']}(the {award['ceremony']}th oscar ceremony)\n"
                        if award['winner']:
                            info += f"        - Winner: {award['name']}\n"
                        else:
                            info += f"        - Nominee(not win): {award['name']}\n"
            info += "\n"
        for person_id in person_ids:
            person_info = self.movie_tool.get_person_info_by_id(person_id)
            info += f"#### Some information of {person_info['name']}\n"
            info += f"- Birthday: {person_info['birthday']}\n"
            if 'acted_movies' in person_info:
                acted_movies = person_info['acted_movies']
                if len(acted_movies) > 0:
                    info += f"- Acted {len(acted_movies)} Movies:\n"
                    for movie in acted_movies:
                        movie = self.movie_tool.get_movie_info_by_id(movie)
                        if movie is None:
                            continue
                        if movie['title'] == movie['original_title']:
                            info += f"    - {movie['title']}\n"
                        else:
                            info += f"    - {movie['title']} ({movie['original_title']})\n"
            if 'directed_movies' in person_info:
                directed_movies = person_info['directed_movies']
                if len(directed_movies) > 0:
                    info += f"- Directed {len(directed_movies)} Movies:\n"
                    for movie in directed_movies:
                        movie = self.movie_tool.get_movie_info_by_id(movie)
                        if movie is None:
                            continue
                        if movie['title'] == movie['original_title']:
                            info += f"    - {movie['title']}\n"
                        else:
                            info += f"    - {movie['title']} ({movie['original_title']})\n"
            if "oscar_awards" in person_info:
                oscar_awards = person_info['oscar_awards']
                if len(oscar_awards) > 0:
                    info += f"- Oscar Awards:\n"
                    for award in oscar_awards:
                        info += f"    - Category: {award['category']}\n"
                        info += f"        - Year: {award['year_ceremony']}(the {award['ceremony']}th oscar ceremony)\n"
                        info += f"        - Movie: {award['film']}\n"
                        if award['winner']:
                            info += f"        - Win or nominate: win\n"
                        else:
                            info += f"        - Win or nominate: nominate\n"
            info += "\n"
        years = re.findall(r'\d{4}', query)
        if len(years) > 0:
            year = years[0]
            if year >= "1990" and year <= "2021":
                info += f"#### Some information of Oscar Awards in {year}:\n"
                year_info = self.movie_tool.get_year_info(year)
                if year_info is not None:
                    awards = year_info['oscar_awards']
                    categories = set()
                    for award in awards:
                        categories.add(award['category'])
                    for category in categories:
                        info += f"- {category}\n"
                        for award in awards:
                            if award['category'] == category and award['winner']:
                                info += f"    - Winner: {award['name']} for {award['film']}\n"
                info += "\n"
        return info

    def get_music_info(self, query, query_time, matched_entities):
        song_names = matched_entities['song']
        artist_names = matched_entities['person']
        band_names = matched_entities['band']
        query_date = query_time[6:10] + "-" + query_time[0:2] + "-" + query_time[3:5]
        years = re.findall(r'\d{4}', query)
        if "last year" in query:
            years = [str(int(query_date[:4]) - 1)]
        info = ""
        # Song
        for song_name in song_names:
            info += f"#### Some Basic Information of the Song: {song_name}\n"
            author = self.music_tool.get_song_author(song_name)
            if author is not None:
                info += f"- Author: {author}\n"
            release_date = self.music_tool.get_song_release_date(song_name)
            if release_date is not None:
                info += f"- Release Date: {release_date}\n"
            release_country = self.music_tool.get_song_release_country(song_name)
            if release_country is not None:
                info += f"- Release Country: {release_country}\n"
            award_count = self.music_tool.get_grammy_award_count_by_song(song_name)
            if award_count is not None:
                info += f"- Grammy Award Count: {award_count}\n"
            info += "\n"
        # Artist
        for artist_name in artist_names:
            info += f"#### Some Basic Information of the Artist: {artist_name}\n"
            birth_place = self.music_tool.get_artist_birth_place(artist_name)
            if birth_place is not None:
                info += f"- Birth Place: {birth_place}\n"
            birth_date = self.music_tool.get_artist_birth_date(artist_name)
            if birth_date is not None:
                info += f"- Birth Date: {birth_date}\n"
            life_span = self.music_tool.get_lifespan(artist_name)
            if life_span[1] is not None:
                info += f"- Life Span: {life_span[0]} to {life_span[1]}\n"
            work_list = self.music_tool.get_artist_all_works(artist_name)
            if work_list is not None and len(work_list) > 0:
                work_list = list(set(work_list))
                date2work = defaultdict(list)
                dates = set()
                works = []
                for work in work_list:
                    work_release_date = self.music_tool.get_song_release_date(work)
                    if work_release_date is not None and work_release_date < query_date:
                        date2work[work_release_date].append(work)
                        dates.add(work_release_date)
                        works.append(work)
                dates = list(dates)
                dates.sort(reverse=True)
                info += f"- First Work:\n"
                info += f"    - {dates[-1]}: {date2work[dates[-1]]}\n"
                if len(years) == 1:
                    year = years[0]
                    if year >= dates[-1]:
                        works_year_info = ""
                        works_year = []
                        for date in dates:
                            if date[:4] == year:
                                for work in date2work[date]:
                                    works_year_info += f"    - {date}: {work}\n"
                                    works_year.append(work)
                        if works_year_info != "":
                            info += f"- Some Works Released in {year}:\n"
                            info += works_year_info
                            info += f"- Total Works Released in {year}: {len(works_year)}\n"
                        else:
                            info += f"- No Works Released in {year}\n"
                if len(years) == 2:
                    year1, year2 = years
                    (year1, year2) = (year1, year2) if year1 < year2 else (year2, year1)
                    if year1 >= dates[-1]:
                        works_year_info = ""
                        works_year = []
                        for date in dates:
                            if date[:4] >= year1 and date[:4] <= year2:
                                for work in date2work[date]:
                                    works_year_info += f"    - {date}: {work}\n"
                                    works_year.append(work)
                        if works_year_info != "":
                            info += f"- Some Works Released from {year1} to {year2}:\n"
                            info += works_year_info
                            info += f"- Total Works Released from {year1} to {year2}: {len(works_year)}\n"
                        else:
                            info += f"- No Works Released from {year1} to {year2}\n"
                else:
                    info += f"- Some Recent Works(Sorted by release date):\n"
                    for date in dates[:5]:
                        for work in date2work[date]:
                            info += f"    - {date}: {work}\n"
                    if len(dates) > 5:
                        info += "    - ...\n"
                    info += f"- Total Works: {len(works)}\n"
            award_count = self.music_tool.get_grammy_award_count_by_artist(artist_name)
            if award_count is not None and award_count > 0:
                info += f"- Grammy Award Count: {award_count}\n"
            award_dates = self.music_tool.get_grammy_award_date_by_artist(artist_name)
            if award_dates is not None and len(award_dates) > 0:
                award_dates.sort()
                info += f"- Grammy Award Winning Years: {', '.join([str(year) for year in award_dates])}\n"
            if award_count is not None and award_count > 0:
                info += f"- Note: Nominations not take into account.\n"
            info += "\n"
        # Band
        for band_name in band_names:
            members = self.music_tool.get_members(band_name)
            if members is not None and len(members) > 0 and "first" not in query and "founding" not in query and "original" not in query:
                info += f"#### Some Basic Information of the Band: {band_name}\n"
                members_ = ", ".join(members)
                info += f"- Current Members: {members_}\n"
                info += f"- Num of Current Members: {len(members)}\n"
            info += "\n"
        # Grammy
        if len(years) == 1:
            year = years[0]
            if year >= "1958" and year <= "2019":
                info += f"#### Some information of Grammy Awards in {year}:\n"
                best_artists = self.music_tool.get_grammy_best_artist_by_year(year)
                best_songs = self.music_tool.get_grammy_best_song_by_year(year)
                best_albums = self.music_tool.get_grammy_best_album_by_year(year)
                if len(best_artists) > 0:
                    for best_artist in best_artists:
                        info += f"- Best New Artist: {best_artist}\n"
                        info += f"    - Birth Place: {self.music_tool.get_artist_birth_place(best_artist)}\n"
                        info += f"    - Birth Date: {self.music_tool.get_artist_birth_date(best_artist)}\n"
                if len(best_songs) > 0:
                    for best_song in best_songs:
                        info += f"- Best Song: {best_song}\n"
                        info += f"    - Release Date: {self.music_tool.get_song_release_date(best_song)}\n"
                        info += f"    - Release Country: {self.music_tool.get_song_release_country(best_song)}\n"
                if len(best_albums) > 0:
                    for best_album in best_albums:
                        info += f"- Best Album: {best_album}\n"
        if len(years) == 2 and "gramm" in query:
            year1, year2 = years
            (year1, year2) = (year1, year2) if year1 < year2 else (year2, year1)
            if year1 >= "1958" and year2 <= "2019":
                info += f"#### Some information of Grammy Awards from {year1} to {year2}:\n"
                for year in range(int(year1), int(year2) + 1):
                    best_artist = self.music_tool.get_grammy_best_artist_by_year(str(year))
                    best_song = self.music_tool.get_grammy_best_song_by_year(str(year))
                    best_album = self.music_tool.get_grammy_best_album_by_year(str(year))
                    if best_artist is not None:
                        info += f"- {year}: Best New Artist: {', '.join(best_artist)}\n"
                    if best_song is not None:
                        info += f"- {year}: Best Song: {', '.join(best_song)}\n"
                    if best_album is not None:
                        info += f"- {year}: Best Album: {', '.join(best_album)}\n"
                info += "\n"
        return info
    
    def get_symbol_stock_date_info(self, symbol, date):
        info = ""
        stock_info = self.finance_tool.get_price(symbol, date)
        if stock_info is not None:
            weekday = datetime.datetime.strptime(date, "%Y-%m-%d").weekday()
            weekday = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][weekday]
            info += f"- Stock Price of {date}({weekday})\n"
            # info += f"- Stock Price of {date}\n"
            # 保留两位小数（四舍五入）
            info += f"    - Open: ${stock_info['Open']:,.2f}\n"
            info += f"    - Close: ${stock_info['Close']:,.2f}\n"
            info += f"    - High: ${stock_info['High']:,.2f}\n"
            info += f"    - Low: ${stock_info['Low']:,.2f}\n"
            info += f"    - Volume: {stock_info['Volume']:,}\n"
        return info

    def get_symbol_stock_dates_info(self, symbol, dates, date_str, query):
        info = ""
        stock_dates_info = [self.finance_tool.get_price(symbol, date) for date in dates]
        opens = [stock_date_info['Open'] for stock_date_info in stock_dates_info if stock_date_info is not None]
        closes = [stock_date_info['Close'] for stock_date_info in stock_dates_info if stock_date_info is not None]
        highs = [stock_date_info['High'] for stock_date_info in stock_dates_info if stock_date_info is not None]
        lows = [stock_date_info['Low'] for stock_date_info in stock_dates_info if stock_date_info is not None]
        volumes = [stock_date_info['Volume'] for stock_date_info in stock_dates_info if stock_date_info is not None]
        
        # 过滤掉 0.01
        for i in range(len(opens)):
            if opens[i] == 0.01 or closes[i] == 0.01 or highs[i] == 0.01 or lows[i] == 0.01:
                return ""
        if len(opens) == 0:
            return ""

        # 先保留两位小数
        opens = [round(open_, 2) for open_ in opens]
        closes = [round(close, 2) for close in closes]
        highs = [round(high, 2) for high in highs]
        lows = [round(low, 2) for low in lows]

        average_open = sum(opens) / len(opens) if len(opens) > 0 else 0
        average_close = sum(closes) / len(closes) if len(closes) > 0 else 0
        average_high = sum(highs) / len(highs) if len(highs) > 0 else 0
        average_low = sum(lows) / len(lows) if len(lows) > 0 else 0
        average_volume = sum(volumes) / len(volumes) if len(volumes) > 0 else 0
        total_volume = sum(volumes)
        highest = max(highs) if len(highs) > 0 else 0
        lowest = min(lows) if len(lows) > 0 else 0
        overall_rise = closes[-1] - opens[0]
        company_name = self.finance_tool.symbol2name[symbol]
        if "average" not in query and "basis" not in query and "mean" not in query and "total" not in query and "daily" not in query:
            info += f"#### Some Information of {company_name} ({symbol})'s Stock Price {date_str}\n"
            info += f"- Open: ${opens[0]:,.2f}\n"
            info += f"- Close: ${closes[-1]:,.2f}\n"
            info += f"- High: ${highest:,.2f}\n"
            info += f"- Low: ${lowest:,.2f}\n"
            info += f"- Overall Rise: ${overall_rise:,.2f}\n"
            info += f"- Volume: {total_volume:,d}\n"
            info += "\n"
        info += f"#### Some Information of {company_name} ({symbol})'s Average Stock Price {date_str} (On a daily basis)\n"
        info += f"- Average Open {date_str}: ${average_open:,.2f}\n"
        info += f"- Average Close {date_str}: ${average_close:,.2f}\n"
        info += f"- Average High {date_str}: ${average_high:,.2f}\n"
        info += f"- Average Low {date_str}: ${average_low:,.2f}\n"
        info += f"- Average Volume {date_str}: {average_volume:,.2f}\n"
        info += "\n"

        return info
    
    def get_symbol_stock_dates_other_info(self, symbol, dates, date_str):
        info = ""
        open_higher = []
        close_higher = []
        open_lower = []
        close_lower = []
        trading_days = self.finance_tool.get_price_history(symbol)
        if trading_days is not None:
            trading_days = list(trading_days.keys())
            trading_days.sort(reverse=True) 
            dates = [date for date in dates if date + " 00:00:00 EST" in trading_days]
            if len(dates) == 0:
                return ""
            last_date = None
            for trading_day in trading_days:
                if trading_day[:10] < min(dates):
                    last_date = trading_day[:10]
                    break
            if last_date is None:
                return ""
            dates.sort()
            for date in dates:
                stock_info = self.finance_tool.get_price(symbol, date)
                last_stock_info = self.finance_tool.get_price(symbol, last_date)
                if stock_info is not None and last_stock_info is not None:
                    if round(stock_info['Open'],2) > round(last_stock_info['Close'],2):
                        open_higher.append(date)
                    elif round(stock_info['Open'],2) < round(last_stock_info['Close'],2):
                        open_lower.append(date)
                    if round(stock_info['Close'],2) > round(stock_info['Open'],2):
                        close_higher.append(date)
                    elif round(stock_info['Close'],2) < round(stock_info['Open'],2):
                        close_lower.append(date)
                    last_date = date
            info += f"#### Some Other Information of {symbol}'s Stock Price {date_str}\n"
            info += f"- Open Price Higher Than Last Close Price:\n"
            info += f"    - {len(open_higher)} Days: {', '.join(open_higher)}\n"
            info += f"- Open Price Lower Than Last Close Price:\n"
            info += f"    - {len(open_lower)} Days: {', '.join(open_lower)}\n"
            info += f"- Close Price Higher Than Open Price:\n"
            info += f"    - {len(close_higher)} Days: {', '.join(close_higher)}\n"
            info += f"- Close Price Lower Than Open Price:\n"
            info += f"    - {len(close_lower)} Days: {', '.join(close_lower)}\n"
            info += "\n"
        return info

    def get_symbol_basis_info(self, symbol):
        info = ""
        company_name = self.finance_tool.symbol2name[symbol]
        info += f"#### Some information of {company_name} ({symbol})\n"
        market_capitalization = self.finance_tool.get_market_capitalization(symbol)
        if market_capitalization is not None:
            info += f"- Market Capitalization: ${market_capitalization:,.2f}\n"
        eps = self.finance_tool.get_eps(symbol)
        if eps is not None:
            try:
                eps = float(eps)
                info += f"- Earnings Per Share: {eps:,.2f}\n"
            except:
                pass
        pe_ratio = self.finance_tool.get_pe_ratio(symbol)
        if pe_ratio is not None:
            try:
                pe_ratio = float(pe_ratio)
                info += f"- Price/Earnings Ratio: {pe_ratio:,.2f}\n"
            except:
                pass
        other_info = self.finance_tool.get_all_info(symbol)
        if other_info is not None:
            info += f"- Other Information\n"
            keys = ['dividendYield', 'totalRevenue']
            for key in other_info:
                if key in keys:
                    info += f"    - {key}: {other_info[key]}\n"
        info += "\n"
        return info
    
    def get_finance_info(self, query, query_time, matched_entities):
        query = query.replace("the last day", "yesterday")
        symbols = matched_entities['symbol']
        if symbols == []:
            symbols = self.finance_tool.get_ticker_names(query)
        if symbols == []:
            return ""
        # date, date_str = find_date_from_text(query_time, query)
        query_date = query_time[6:10] + "-" + query_time[0:2] + "-" + query_time[3:5]
        info = ""
        note_info = ""

        # basis
        for symbol in symbols:
            info += self.get_symbol_basis_info(symbol)

        divid_dates = []
        # dividend
        if "dividend" in query:
            if "year" in query or re.search(r'\d{4}', query) is not None:
                years = re.findall(r'\d{4}', query)
                if "last" in query or "previous" in query or "past" in query or "recent" in query:
                    years.append(str(int(query_date[:4]) - 1))
                elif len(years) == 0:
                    years = [query_date[:4]]
                years = list(set(years))
                for symbol in symbols:
                    company_name = self.finance_tool.symbol2name[symbol]
                    info += f"#### Some Information of {company_name} ({symbol})'s Dividends\n"
                    info += f"- Dividends in {', '.join(years)}\n"
                    for year in years:
                        dividend = self.finance_tool.get_dividends_history_by_year(symbol, year)
                        if dividend is not None and len(dividend) > 0:
                            dividend_dates = list(dividend.keys())
                            dividend_dates.sort()
                            info += f"    - {year}\n"
                            total_dividend = sum(dividend.values())
                            for dividend_date in dividend_dates:
                                info += f"        - {dividend_date[:10]}: ${dividend[dividend_date]:,.2f}\n"
                            info += f"    - Total Dividends Distributed in {year}: ${total_dividend:,.2f}\n"
                        else:
                            info += f"    - {year}: No Dividends Distributed\n"
                            note_info += f"- If ask for the days dividends distributed in {year}, reply `None of the Days`\n"
                    
                    dividend_2023 = self.finance_tool.get_dividends_history_by_year(symbol, "2023")
                    dividend_2022 = self.finance_tool.get_dividends_history_by_year(symbol, "2022")
                    if len(dividend_2023) > 0 and len(dividend_2022) > 0 and len(dividend_2023) == len(dividend_2022):
                        dividend_times_per_year = len(dividend_2023)
                        info += f"- Dividends Distributed Times Per Year: {dividend_times_per_year}\n"
                    info += "\n"

            else:
                for symbol in symbols:
                    company_name = self.finance_tool.symbol2name[symbol]
                    dividend = self.finance_tool.get_dividends_history(symbol)
                    if dividend is not None and len(dividend) > 0:
                        dividend_dates = list(dividend.keys())
                        dividend_dates.sort()
                        info += f"#### Some Information of {company_name} ({symbol})'s Dividends\n"
                        info += f"- First Dividend Distributed\n"
                        info += f"    - {dividend_dates[0][:10]}: ${dividend[dividend_dates[0]]:,.2f}\n"
                        info += f"- Last Dividend Distributed\n"
                        info += f"    - {dividend_dates[-1][:10]}: ${dividend[dividend_dates[-1]]:,.2f}\n"
                        total_dividend = sum(dividend.values())
                        info += f"- Total Dividends Distributed: ${total_dividend:,.2f}\n"
                        info += "\n"
                        divid_dates.append(dividend_dates[-1][:10])
                        divid_dates.append(dividend_dates[0][:10])
                    else:
                        info += f"#### Some Information of {company_name} ({symbol})'s Dividends\n"
                        info += f"- No Dividends Distributed\n"
                        note_info += f"- If ask for the days dividends distributed, reply `None of the Days`\n"
                        info += "\n"

        # stock price
        # 特殊情况处理（week, month, year)等等
        if "week" in query:
            # 匹配月份
            match = re.match(r".*?(\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\b).*?", query)
            match_ = re.match(r".*?(\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b).*?", query)
            # if (match or match_) and extract_date_(query) is None:
            if match or match_:
                if match:
                    month_ = match.group(1)
                    month = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"].index(month_) + 1
                else:
                    month_ = match_.group(1)
                    month = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"].index(month_) + 1
                if "first week" in query:
                    year = re.findall(r'\d{4}', query)
                    if "last year" in query:
                        year = str(int(query_date[:4]) - 1)
                    elif len(year) == 0:
                        year = query_date[:4]
                    else:
                        year = year[0]
                    dates = [f"{year}-{month:02d}-{day:02d}" for day in range(1, 8)]
                    for symbol in symbols:
                        company_name = self.finance_tool.symbol2name[symbol]
                        if self.get_symbol_stock_dates_info(symbol, dates, f"First Week of {month_} {year}", query) != "":
                            if "average" not in query and "basis" not in query and "mean" not in query and "total" not in query and "daily" not in query  and "higher" not in query and "lower" not in query:
                                info += f"#### Some Information of {company_name} ({symbol})'s Stock Price First Week of {month} {year}\n"
                                for date in dates:
                                    info += self.get_symbol_stock_date_info(symbol, date)
                                info += "\n"
                            info += self.get_symbol_stock_dates_info(symbol, dates, f"First Week of {month_} {year}", query)
                            if "higher" in query or "lower" in query:
                                info += self.get_symbol_stock_dates_other_info(symbol, dates, f"First Week of {month_} {year}")
                            info += "\n"
            elif "last" in query or "previous" in query or "past" in query or "recent" in query:
                dates = get_last_week_dates(query_time)
                for symbol in symbols:
                    company_name = self.finance_tool.symbol2name[symbol]
                    if self.get_symbol_stock_dates_info(symbol, dates, "Last Week", query) != "":
                        if "average" not in query and "basis" not in query and "mean" not in query and "total" not in query and "daily" not in query and "higher" not in query and "lower" not in query:
                            info += f"#### Some Information of {company_name} ({symbol})'s Stock Price Last Week\n"
                            for date in dates:
                                info += self.get_symbol_stock_date_info(symbol, date)
                            info += "\n"
                        info += self.get_symbol_stock_dates_info(symbol, dates, "Last Week", query)
                        if "higher" in query or "lower" in query:
                            info += self.get_symbol_stock_dates_other_info(symbol, dates, "Last Week")
                        info += "\n"
            else:
                dates = get_this_week_dates(query_time)
                dates = [date for date in dates if date < query_date]
                for symbol in symbols:
                    company_name = self.finance_tool.symbol2name[symbol]
                    if self.get_symbol_stock_dates_info(symbol, dates, "This Week", query) != "":
                        if "average" not in query and "basis" not in query and "mean" not in query and "total" not in query and "daily" not in query and "higher" not in query and "lower" not in query:
                            info += f"#### Some Information of {company_name} ({symbol})'s Stock Price This Week\n"
                            for date in dates:
                                info += self.get_symbol_stock_date_info(symbol, date)
                            info += "\n"
                        info += self.get_symbol_stock_dates_info(symbol, dates, "This Week", query)
                        if "higher" in query or "lower" in query:
                            info += self.get_symbol_stock_dates_other_info(symbol, dates, "This Week")
                        info += "\n"
        elif "month" in query:
            if "last" in query or "previous" in query or "past" in query or "recent" in query:
                dates = get_last_month_dates(query_time)
                for symbol in symbols:
                    company_name = self.finance_tool.symbol2name[symbol]
                    # info += f"#### Some Information of {company_name} ({symbol})'s Stock Price Last Month\n"
                    # for date in dates[:3]:
                    #     info += self.get_symbol_stock_date_info(symbol, date)
                    # info += "...\n"
                    # for date in dates[-3:]:
                    #     info += self.get_symbol_stock_date_info(symbol, date)
                    if self.get_symbol_stock_dates_info(symbol, dates, "Last Month", query) != "":
                        info += self.get_symbol_stock_dates_info(symbol, dates, "Last Month", query)
                        if "higher" in query or "lower" in query:
                            info += self.get_symbol_stock_dates_other_info(symbol, dates, "Last Month")
                        info += "\n"
            else:
                dates = get_this_month_dates(query_time)
                for symbol in symbols:
                    company_name = self.finance_tool.symbol2name[symbol]
                    if self.get_symbol_stock_dates_info(symbol, dates, "This Month", query) != "":
                        info += self.get_symbol_stock_dates_info(symbol, dates, "This Month", query)
                        if "higher" in query or "lower" in query:
                            info += self.get_symbol_stock_dates_other_info(symbol, dates, "This Month")
                        info += "\n"
        elif "year" in query:
            if "last" in query or "previous" in query or "past" in query or "recent" in query:
                pass
            else:
                year = query_date[:4]
                date = f"{year}-01-01"
                for symbol in symbols:
                    company_name = self.finance_tool.symbol2name[symbol]
                    stock_info = None
                    while date < query_date and stock_info is None:
                        stock_info = self.finance_tool.get_price(symbol, date)
                        date = (datetime.datetime.strptime(date, "%Y-%m-%d") + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
                    stock_info_now = self.finance_tool.get_price(symbol, query_date)
                    if stock_info is not None and stock_info_now is not None:
                        info += f"#### Some Information of {company_name} ({symbol})'s Stock Price This Year(Until Now)\n"
                        info += f"- Stock Price First Trading Day This Year\n"
                        info += f"    - Open: ${stock_info['Open']:,.2f}\n"
                        info += f"    - Close: ${stock_info['Close']:,.2f}\n"
                        info += f"    - High: ${stock_info['High']:,.2f}\n"
                        info += f"    - Low: ${stock_info['Low']:,.2f}\n"
                        info += f"    - Volume: {stock_info['Volume']:,}\n"
                        info += f"- Stock Price Today\n"
                        info += f"    - Open: ${stock_info_now['Open']:,.2f}\n"
                        info += f"    - Close: ${stock_info_now['Close']:,.2f}\n"
                        info += f"    - High: ${stock_info_now['High']:,.2f}\n"
                        info += f"    - Low: ${stock_info_now['Low']:,.2f}\n"
                        info += f"    - Volume: {stock_info_now['Volume']:,}\n"
                        info += f"Overall Rise: ${stock_info_now['Close'] - stock_info['Open']:,.2f}\n"
                        info += "\n"
        else:
            dates, dates_str = find_date_from_text_all(query_time, query)
            if len(dates) == 0:
                date = extract_date_(query)
                if date is not None:
                    dates = [date]
                else:
                    dates = [query_date]
            for date, date_str in zip(dates, dates_str):
                if date_str != "today" and date_str != "yesterday":
                    note_info += f"- {date_str} of {query_date} is {date}\n"
            if "trading" in query and re.search(r"\bday\b", query) or "last trading" in query:
                trading_days = self.finance_tool.get_price_history(symbols[0])
                if trading_days is not None:
                    if "first trading day of" in query:
                        year = re.findall(r'\d{4}', query)
                        if len(year) == 0:
                            year = query_date[:4]
                        else:
                            year = year[0]
                        match = re.match(r".*?(\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\b).*?", query)
                        match_ = re.match(r".*?(\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b).*?", query)
                        # if (match or match_) and extract_date_(query) is None:
                        if match or match_:
                            if match:
                                month_ = match.group(1)
                                month = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"].index(month_) + 1
                            else:
                                month_ = match_.group(1)
                                month = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"].index(month_) + 1
                            date = f"{year}-{month:02d}-01"
                            trading_days = list(trading_days.keys())
                            trading_days.sort()
                            for trading_day in trading_days:
                                if trading_day[:10] >= date:
                                    date = trading_day[:10]
                                    dates = [date]
                                    break
                            note_info += f"- First Trading Day of {month_} {year} is {date}\n"
                    else:
                        trading_days = list(trading_days.keys())
                        trading_days.sort(reverse=True) 
                        for trading_day in trading_days:
                            if trading_day[:10] < query_date:
                                date = trading_day[:10]
                                dates = [date]
                                break
                        note_info += f"- Last Trading Day of {query_date} is {date}\n"
            dates.extend(divid_dates)
            for symbol in symbols:
                company_name = self.finance_tool.symbol2name[symbol]
                info_ = ""
                for date in dates:
                    if date != query_date:
                        info_ += self.get_symbol_stock_date_info(symbol, date)
                if query_date in dates:
                    if "close" in query or "high" in query or "low" in query:
                        info_ += self.get_symbol_stock_date_info(symbol, query_date)
                    else:
                        stock_details = self.finance_tool.get_detailed_price_history(symbol)
                        if stock_details is not None:
                            stock_details_today_keys = [key for key in stock_details.keys() if key[:10] == query_date]
                            if len(stock_details_today_keys) > 0:
                                info += f"#### Some Information of {company_name} ({symbol})'s Stock Price Today\n"
                                stock_details_today_keys.sort(reverse=True)
                                open_price = stock_details[stock_details_today_keys[-1]]['Open']
                                open_time = stock_details_today_keys[-1]
                                current_time = (datetime.datetime.strptime(query_time, "%m/%d/%Y, %H:%M:%S PT") + datetime.timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S EST')
                                for key in stock_details_today_keys:
                                    if key < current_time:
                                        latest_price = stock_details[key]['Close']
                                        latest_time = key
                                        break
                                if key == stock_details_today_keys[-1]:
                                    info += "- Market is still close, no information today\n"
                                else:
                                    info += f"- Open Price({open_time}): ${open_price:,.2f}\n"
                                    info += f"- Latest Price({latest_time}): ${latest_price:,.2f}\n"
                                info += "\n"
                if len(info_) > 0:
                    info += f"#### Some Information of {company_name} ({symbol})'s Stock Price\n"
                    info += info_
                    info += "\n"
                info += "\n"
        if len(info) > 0 and len(note_info) > 0:
            info += "Note:\n" + note_info
        return info
    
    def get_finance_info_old(self, query, query_time, matched_entities):
        symbols = matched_entities['symbol']
        if symbols == []:
            return ""
        date, date_str = find_date_from_text(query_time, query)
        query_date = query_time[6:10] + "-" + query_time[0:2] + "-" + query_time[3:5]
        info = ""
        if date is None:
            date = query_date
        if date_str is not None and date_str != "today" and date_str != "yesterday":
            info += f"{date_str} of {query_date} is {date}\n"
        if "trading day" in query:
            trading_days = self.finance_tool.get_price_history(symbols[0])
            if trading_days is not None:
                trading_days = list(trading_days.keys())
                trading_days.sort(reverse=True) 
                for trading_day in trading_days:
                    if trading_day < date:
                        date = trading_day[:10]
                        break
                info += f"Last Trading Day of  {query_date} is {date}\n"
        for symbol in symbols:
            company_name = self.finance_tool.symbol2name[symbol]
            info += f"#### Some information of {company_name} ({symbol})\n"
            stock_info = self.finance_tool.get_price(symbol, date)
            if stock_info is not None:
                info += f"- Stock Price of {date}\n"
                # 保留两位小数（四舍五入）
                info += f"    - Open: {stock_info['Open']:.2f}\n"
                info += f"    - Close: {stock_info['Close']:.2f}\n"
                info += f"    - High: {stock_info['High']:.2f}\n"
                info += f"    - Low: {stock_info['Low']:.2f}\n"
                info += f"    - Volume: {stock_info['Volume']}\n"
            dividend_info = self.finance_tool.get_dividends_history(symbol)
            if dividend_info is not None and len(dividend_info) > 0:
                dividend_dates = list(dividend_info.keys())
                dividend_dates.sort()
                info += f"- Dividends History({dividend_dates[0][:10]} to {dividend_dates[-1][:10]})\n"
                if len(dividend_dates) <= 20:
                    for dividend_date in dividend_dates:
                        info += f"    - {dividend_date[:10]}: {dividend_info[dividend_date]}\n"
                else:
                    for dividend_date in dividend_dates[:10]:
                        info += f"    - {dividend_date[:10]}: {dividend_info[dividend_date]}\n"
                    info += "    - ...\n"
                    for dividend_date in dividend_dates[-10:]:
                        info += f"    - {dividend_date[:10]}: {dividend_info[dividend_date]}\n"
            else:
                info += "- No Dividends History\n"
            market_capitalization = self.finance_tool.get_market_capitalization(symbol)
            if market_capitalization is not None:
                info += f"- Market Capitalization: {market_capitalization:.2f}\n"
            eps = self.finance_tool.get_eps(symbol)
            if eps is not None:
                info += f"- Earnings Per Share: {eps:.2f}\n"
            pe_ratio = self.finance_tool.get_pe_ratio(symbol)
            if pe_ratio is not None:
                info += f"- Price/Earnings Ratio: {pe_ratio:.2f}\n"
            other_info = self.finance_tool.get_all_info(symbol)
            if other_info is not None:
                info += f"- Other Information\n"
                keys = ['dividendYield', 'totalRevenue']
                for key in other_info:
                    if key in keys:
                        info += f"    - {key}: {other_info[key]}\n"
            info += "\n"

        return info


    def get_soccer_game_info(self, query, game, soccer_team, game_date=None):
        info = ""
        for _, value in game.items():
            if value['date'] == game_date or game_date is None:
                if game_date is None:
                    game_date = value['date']
                opponent = value['opponent']
                venue = value['venue']
                time = value['time']
                result = value['result']
                day_ = value['day']
                round_ = value['round']
                if venue == "home":
                    info += f"- {soccer_team} vs {opponent} on {game_date}\n"
                else:
                    info += f"- {opponent} vs {soccer_team} on {game_date}\n"
                if time is not None:
                    info += f"    - Time: {time}\n"
                if day_ is not None:
                    info += f"    - Day: {day_}\n"
                if round_ is not None:
                    info += f"    - Round: {round_}\n"
                info += f"    - Venue: {venue}\n"
                if result is not None:
                    info += f"    - Result: {result}\n"
                if value['GF'] is not None and value['GA'] is not None:
                    info += f"    - Goal For: {value['GF']}\n"
                    info += f"    - Goal Against: {value['GA']}\n"
                if "attendance" in query and value['Attendance'] is not None:
                    info += f"    - Attendance: {value['Attendance']}\n"
                if "referee" in query and value['Referee'] is not None:
                    info += f"    - Referee: {value['Referee']}\n"
                if "captain" in query and value['Captain'] is not None:
                    info += f"    - Captain: {value['Captain']}\n"
                if "formation" in query and value['Formation'] is not None:
                    info += f"    - Formation: {value['Formation']}\n"
        return info
    
    def get_sports_info(self, query, query_time, matched_entities):
        nba_teams = matched_entities['nba team']
        soccer_teams = matched_entities['soccer team']
        if nba_teams == []:
            nba_teams = self.sports_tool.get_nba_teams(query)
        if soccer_teams == []:
            soccer_teams = self.sports_tool.get_soccer_teams(query)
        nba_players = matched_entities['nba player']
        soccer_players = matched_entities['soccer player']
        year, month, day = extract_date(query)
        query_date = query_time[6:10] + "-" + query_time[0:2] + "-" + query_time[3:5]
        info = ""
        if year is None:
            date, date_str = find_date_from_text(query_time, query)
            if date is None:
                date = query_date
            if date_str is not None and date_str != "today" and date_str != "yesterday":
                info += f"{date_str} of {query_date} is {date}\n"
        elif month is not None and day is not None:
            date = f"{year}-{month}-{day}"
        elif month is not None and day is None:
            date = f"{year}-{month}"
        else:
            date = year
        # NBA
        for nba_team in nba_teams:
            if date is not None:
                games = self.sports_tool.nba_get_games_on_date(date, nba_team)
                if games is not None:
                    game_indexs, game_dates = [], []
                    for game_index, game_date in games['game_date'].items():
                            game_indexs.append(game_index)
                            game_dates.append(game_date[:10])
                    # 按照 game_date 降序排列
                    game_dates, game_indexs = zip(*sorted(zip(game_dates, game_indexs), reverse=True))
                    if len(game_dates) == 1:
                        info += f"#### Some information of {nba_team} on {game_dates[0]}\n"
                        info += f"- {games['team_name_away'][game_indexs[0]]} vs {games['team_name_home'][game_indexs[0]]}\n"
                        info += f"    - Final Score: {int(games['pts_away'][game_index])} : {int(games['pts_home'][game_index])}\n"
                        winner = games['team_name_away'][game_indexs[0]] if games['pts_away'][game_indexs[0]] > games['pts_home'][game_indexs[0]] else games['team_name_home'][game_indexs[0]]
                        info += f"    - Winner: {winner}\n"
                        info += f"    - Season Type: {games['season_type'][game_indexs[0]]}\n"
                    if len(game_dates) >= 2:
                        info += f"#### Some information of {nba_team} during {date}\n"
                        num_wins = 0
                        num_losses = 0
                        num_homes = 0
                        num_aways = 0
                        num_win_homes = 0
                        num_win_aways = 0
                        total_points = 0
                        for i, (game_index, game_date) in enumerate(zip(game_indexs, game_dates)):
                            winner = games['team_name_away'][game_index] if games['pts_away'][game_index] > games['pts_home'][game_index] else games['team_name_home'][game_index]
                            if i < 5:
                                info += f"- {games['team_name_away'][game_index]} vs {games['team_name_home'][game_index]} on {game_date}\n"
                                info += f"    - Final Score: {int(games['pts_away'][game_index])} : {int(games['pts_home'][game_index])}\n"
                                info += f"    - Winner: {winner}\n"
                                info += f"    - Season Type: {games['season_type'][game_index]}\n"
                            if i == 5:
                                info += "- ...\n"
                            if winner == nba_team:
                                num_wins += 1
                            else:
                                num_losses += 1
                            if games['team_name_home'][game_index] == nba_team:
                                num_homes += 1
                                total_points += games['pts_home'][game_index]
                            else:
                                num_aways += 1
                                total_points += games['pts_away'][game_index]
                            if games['team_name_home'][game_index] == nba_team and winner == nba_team:
                                num_win_homes += 1
                            if games['team_name_away'][game_index] == nba_team and winner == nba_team:
                                num_win_aways += 1
                        info += f"- Total Wins: {num_wins}\n"
                        info += f"- Total Losses: {num_losses}\n"
                        info += f"- Total Home Games: {num_homes}\n"
                        info += f"- Total Away Games: {num_aways}\n"
                        info += f"- Total Home Wins: {num_win_homes}\n"
                        info += f"- Total Away Wins: {num_win_aways}\n"
                        info += f"- Total Home losses: {num_homes - num_win_homes}\n"
                        info += f"- Total Away losses: {num_aways - num_win_aways}\n"
                        info += f"- Total Games: {num_wins + num_losses}\n"
                        info += f"- Total Points Scored: {int(total_points)}"
                    info += "\n"
                        
        # Soccer
        soccer_leagues = self.sports_tool.get_soccer_leagues(query)
        have_league = len(soccer_leagues) == 1
        for soccer_team in soccer_teams:
            # 特殊情况处理（week，month)
            if "week" in query:
                last_week = get_last_week_dates(query_time)
                this_week = get_this_week_dates(query_time)
                last_week_games = {}
                for d in last_week:
                    games = self.sports_tool.soccer_get_games_on_date(d, soccer_team)
                    if games is not None:
                        for k, v in games.items():
                            last_week_games[k] = v
                this_week_games = {}
                for d in this_week:
                    games = self.sports_tool.soccer_get_games_on_date(d, soccer_team)
                    if games is not None:
                        for k, v in games.items():
                            this_week_games[k] = v
                if last_week_games == {}:
                    info += f"- {soccer_team} have no game last week\n"
                    info += f"    - Note: If ask for status of last week's game, please respond with `invlaid question`.\n"
                else:
                    info += f"#### Some information of {soccer_team} last week\n"
                    info += self.get_soccer_game_info(query, last_week_games, soccer_team)
                if this_week_games == {}:
                    info += f"- {soccer_team} have no game this week\n"
                    info += f"    - Note: If ask for status of this week's game, please respond with `invlaid question`.\n"
                else:
                    info += f"#### Some information of {soccer_team} this week\n"
                    info += self.get_soccer_game_info(query, this_week_games, soccer_team)
                info += "\n"
                continue
            elif "month" in query:
                last_month = get_last_month_dates(query_time)
                this_month = get_this_month_dates(query_time)
                last_month_games = {}
                for d in last_month:
                    games = self.sports_tool.soccer_get_games_on_date(d, soccer_team)
                    if games is not None:
                        for k, v in games.items():
                            last_month_games[k] = v
                this_month_games = {}
                for d in this_month:
                    games = self.sports_tool.soccer_get_games_on_date(d, soccer_team)
                    if games is not None:
                        for k, v in games.items():
                            this_month_games[k] = v
                if last_month_games == {}:
                    info += f"- {soccer_team} have no game last month\n"
                    info += f"    - Note: If ask for status of last month's game, please respond with `invlaid question`.\n"
                else:
                    info += f"#### Some information of {soccer_team} last month\n"
                    info += self.get_soccer_game_info(query, last_month_games, soccer_team)
                if this_month_games == {}:
                    info += f"- {soccer_team} have no game this month\n"
                    info += f"    - Note: If ask for status of this month's game, please respond with `invlaid question`.\n"
                else:
                    info += f"#### Some information of {soccer_team} this month\n"
                    info += self.get_soccer_game_info(query, this_month_games, soccer_team)
                info += "\n"
                continue
            # 无指定日期
            elif date == query_date:
                games = self.sports_tool.soccer_get_games_on_date(date[:4], soccer_team)
                games_ = self.sports_tool.soccer_get_games_on_date(str(int(date[:4])-1), soccer_team)
                if games_ is not None and games is not None:
                    for k, v in games_.items():
                        games[k] = v
                elif games_ is not None:
                    games = games_
                if games is not None:
                    game_dates_past = []
                    game_dates_future = []
                    for key, value in games.items():
                        league = self.sports_tool.get_soccer_leagues(key)[0]
                        if have_league and league == soccer_leagues[0] or not have_league:
                            if value['date'] < date:
                                game_dates_past.append(value['date'])
                            if value['date'] > date:
                                game_dates_future.append(value['date'])
                            if value['date'] == date:
                                time = value['time']
                                if time is not None and time > query_time[12:20]:
                                    print(time, query_time[12:20])
                                    game_dates_future.append(value['date'])
                    game_dates_past.sort(reverse=True)
                    game_dates_future.sort()
                    if "past" in query or "previous" in query or "last" in query or "recent" in query and len(game_dates_past) > 0:
                        if have_league:
                            info += f"#### Information of last game played by {soccer_team} in {soccer_leagues[0]}\n"
                        else:
                            info += f"#### Information of last game played by {soccer_team}\n"
                        info += self.get_soccer_game_info(query, games, soccer_team, game_dates_past[0])
                        info += "\n"
                        continue
                    elif "next" in query or "coming" in query or "future" in query and len(game_dates_future) > 0:
                        if have_league:
                            info += f"#### Information of next game played by {soccer_team} in {soccer_leagues[0]}\n"
                        else:
                            info += f"#### Information of next game played by {soccer_team}\n"
                        info += self.get_soccer_game_info(query, games, soccer_team, game_dates_future[0])
                        info += "\n"
                        continue
                    # elif len(game_dates_past) > 0:
                    #     if have_league:
                    #         info += f"#### Some information of recent games played by {soccer_team} in {soccer_leagues[0]}\n"
                    #     else:
                    #         info += f"#### Some information of recent games played by {soccer_team}\n"
                    #     for game_date in game_dates_past[:5]:
                    #         info += self.get_soccer_game_info(query, games, soccer_team, game_date)
            # 有指定日期
            if date is not None:
                games = self.sports_tool.soccer_get_games_on_date(date, soccer_team)
                if games is None:
                    if have_league and len(date) == 10:
                        if "today" in query:
                            info += f"- {soccer_team} have no game today in {soccer_leagues[0]}\n"
                            info += f"    - Note: If ask for status of today's game, please respond with `invlaid question`.\n"
                        elif "yesterday" in query:
                            info += f"- {soccer_team} have no game yesterday in {soccer_leagues[0]}\n"
                            info += f"    - Note: If ask for status of yesterday's game, please respond with `invlaid question`.\n"
                        else:
                            info += f"- {soccer_team} have no game on {date} in {soccer_leagues[0]}\n"
                            info += f"    - Note: If ask for status of {date}'s game, please respond with `invlaid question`.\n"
                    elif have_league and len(date) != 10:
                        info += f"- {soccer_team} have no game during {date} in {soccer_leagues[0]}\n"
                    elif not have_league and len(date) == 10:
                        if "today" in query:
                            info += f"- {soccer_team} have no game today\n"
                            info += f"    - Note: If ask for status of today's game, please respond with `invlaid question`.\n"
                        elif "yesterday" in query:
                            info += f"- {soccer_team} have no game yesterday\n"
                            info += f"    - Note: If ask for status of yesterday's game, please respond with `invlaid question`.\n"
                        else:
                            info += f"- {soccer_team} have no game on {date}\n"
                            info += f"    - Note: If ask for status of {date}'s game, please respond with `invlaid question`.\n"
                    else:
                        info += f"- {soccer_team} have no game during {date}\n"
                        info += f"    - Note: If ask for status of {date}'s game, please respond with `invlaid question`.\n"
                if games is not None:
                    game_dates = []
                    for key, value in games.items():
                        league = self.sports_tool.get_soccer_leagues(key)[0]
                        if have_league and league == soccer_leagues[0] or not have_league:
                            game_dates.append(value['date'])
                    game_dates.sort(reverse=True)
                    if len(game_dates) == 0:
                        if have_league and len(date) == 10:
                            if "today" in query:
                                info += f"- {soccer_team} have no game today in {soccer_leagues[0]}\n"
                                info += f"    - Note: If ask for status of today's game, please respond with `invlaid question`.\n"
                            elif "yesterday" in query:
                                info += f"- {soccer_team} have no game yesterday in {soccer_leagues[0]}\n"
                                info += f"    - Note: If ask for status of yesterday's game, please respond with `invlaid question`.\n"
                            else:
                                info += f"- {soccer_team} have no game on {date} in {soccer_leagues[0]}\n"
                                info += f"    - Note: If ask for status of {date}'s game, please respond with `invlaid question`.\n"
                        elif have_league and len(date) != 10:
                            info += f"- {soccer_team} have no game during {date} in {soccer_leagues[0]}\n"
                            info += f"    - Note: If ask for status of {date}'s game, please respond with `invlaid question`.\n"
                        elif not have_league and len(date) == 10:
                            if "today" in query:
                                info += f"- {soccer_team} have no game today\n"
                                info += f"    - Note: If ask for status of today's game, please respond with `invlaid question`.\n"
                            elif "yesterday" in query:
                                info += f"- {soccer_team} have no game yesterday\n"
                                info += f"    - Note: If ask for status of yesterday's game, please respond with `invlaid question`.\n"
                            else:
                                info += f"- {soccer_team} have no game on {date}\n"
                                info += f"    - Note: If ask for status of {date}'s game, please respond with `invlaid question`.\n"
                        else:
                            info += f"- {soccer_team} have no game during {date}\n"
                    elif len(date) == 10:
                        if have_league:
                            info += f"- Some information of {soccer_team} on {game_dates[0]} in {soccer_leagues[0]}\n"
                        else:
                            info += f"#### Some information of {soccer_team} on {game_dates[0]}\n"
                        info += self.get_soccer_game_info(query, games, soccer_team, game_dates[0])
                    elif len(date) < 10:
                        if have_league:
                            info += f"#### Some information of {soccer_team} during {date} in {soccer_leagues[0]}\n"
                        else:
                            info += f"#### Some information of {soccer_team} during {date}\n"
                        for game_date in game_dates:
                            info += self.get_soccer_game_info(query, games, soccer_team, game_date)
                    info += "\n"
        if len(info) > 0:
            info += """#### Note:
- For NBA, Matchup between two teams is displayed as 'team away vs team home'.
- For NBA, When ask about Final Score, just consider the points scored by the team.
- For Soccer, When ask about total goals of a team, just consider the goals scored by the team(Goal For).
- For Soccer, When ask about win-loss results, possible results are 'Win', 'Loss', 'Draw'."""
        return info
    
    def get_kg_info(self, queries, query_times, domains):
        kg_infos = []
        ner_results = self.ner(queries, domains)
        for query, query_time, domain, ner_result in zip(queries, query_times, domains, ner_results):
            matched_entities = self.name_entity_match(ner_result, domain)
            if domain == "movie":
                kg_info = self.get_movie_info(query, query_time, matched_entities)
            elif domain == "music":
                kg_info = self.get_music_info(query, query_time, matched_entities)
            elif domain == "finance":
                kg_info = self.get_finance_info(query, query_time, matched_entities)
            elif domain == "sports":
                kg_info = self.get_sports_info(query, query_time, matched_entities)
            else:
                kg_info = ""
            kg_infos.append(kg_info)
        return kg_infos