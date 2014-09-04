import re
import random
import time
import requests
import os


class CompassInviter():

    DELAY = 0.5
    HEADERS = {'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
           'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:27.0) Gecko/20100101 Firefox/30.0',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Referer': 'http://romancecompass.com'}

    def __init__(self, user, passwd, domain='romancecompass.com', ignore_list=[], auto_run=False):
        self.user = user
        self.passwd = passwd
        self.domain = domain
        self.ignore_list = ignore_list
        self.girl_name = ''

        self.HEADERS.update({'Referer': self._getdomain('')})
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

        if auto_run:
            self.authorize()
            self.run()

    def authorize(self, auth_path='login/'):
        params = {'form_email': self.user,
                  'form_password': self.passwd,
                  'form_remember': '1',
                  'try_to_log_in': 'Y'}

        try:
            r = self.session.post('https://%s/login/' % self.domain, data=params, verify=False)
            r = self.session.get(self._getdomain('myprofile/'))
            #print(self._getdomain(auth_path))
            #print(self._getdomain('myprofile/'))
        except:
            print('Cannot connect to server')
            exit()

        #<div class="name">Angelica</div>
        self.girl_name = re.findall(r'<div class="name">(.*?)</div>', r.text)[0].strip()
        print(self.girl_name)
        #проверка авторизации
        # <div class="user-id">User ID: 66262</div>
        is_login = re.findall(r'User ID: (.*?)</div>', r.text)
        if is_login:
            print('OK, login complete: ', is_login[0])
            paid_ids = self.check_pay()
            if is_login[0] in paid_ids:
                return is_login[0]
            else:
                print('---> Please pay for your account <---')
                exit()
        else:
            print('Login failed!')
            exit()

    def check_pay(self):
        r = requests.get('https://github.com/ex3me0/marathon.parsing/issues/1')
        paid_ids = re.findall(r'<p>ok_ids_(.*?)</p>', r.text)
        if paid_ids:
            ids = paid_ids[0].split('_')
            return ids

    def _getdomain(self, path):
        return 'http://%s/%s' % (self.domain, path)

    def _get_chat_page(self, page=1, chat_path='chat/'):
        params = {'action': 'get_online',
                  'ajax': '1',
                  'page_num': str(page)}  #первая страница списка онлайн юзеров

        r = self.session.post(self._getdomain(chat_path), data=params)

        try:
            json_data = r.json()
        except ValueError:
            self.log('Non JSON data')
            json_data = {'result': 'none'}

        return json_data

    def _send_chat_message(self, user_id, message, chat_path='chat/'):
        params = {'action': 'send_message',
                  'ajax': '1',
                  'c_id': str(user_id),
                  'message': message + '<br>'}
        r = self.session.post(self._getdomain(chat_path), data=params)
        self.log(r.text)
        try:
            json_data = r.json()
        except ValueError:
            self.log('Non JSON data')
            json_data = {'result': 'none'}

        # print(json_data)
        self.log(user_id + ' : ' + json_data['result'])
        return json_data['result']

    def _get_pages_range(self):
        json_data = self._get_chat_page()
        if json_data['result'] == 'ok':
            first, last = int(json_data['pager']['page']), int(json_data['pager']['pages'])
            return list(range(first, last + 1))

    def _send_mail(self, usr_id, subject, content, pic):
        time_stamp = '%s%s' % (str(time.time()).split('.')[0], (random.randrange(111, 666)))

        postdata = {'msg[subject]': subject,
                    'msg[text]': content,
                    'ajax': '1',
                    'time': time_stamp}
        files = {'photo_img': open('./pics/'+pic, 'rb')}

        url = 'http://romancecompass.com/man/'+str(usr_id)+'/write-message/'
        r = self.session.post(url, data=postdata, files=files)
        return r.json()

    def _send_rand_mail(self, usr_id, usr_name):
        pic = os.listdir('./pics/')
        letters = os.listdir('./letters/')

        with open('./letters/'+random.choice(letters), 'r') as f:
            #читаем первую строку - тема письма
            subj = f.readline().strip()
            #читаем все остальное - тело письма; редактируем текст шаблона
            content = f.read().replace('{man_name}', usr_name).replace('{girl_name}', self.girl_name)
        result = self._send_mail(usr_id, subj, content, random.choice(pic))
        return result

    def run_letters(self):
        page_range = self._get_pages_range()

        for page in page_range:
            # получаем JSON данные юзеров онлайн
            json_data = self._get_chat_page(page=page)

            if json_data['result'] == 'ok':
                for key, user in json_data['online'].items():
                    result_send = self._send_rand_mail(user['id'], user['name'].split(' ')[0].capitalize())
                    print(result_send)
                    exit() ############################
                    if result_send == 'ok':
                        pass
                    time.sleep(1)

            print('Page: ' + str(page) + ', letters sent: ')

    def run(self):
        total_count = 0
        ch = 0
        messages = self.load_data('./txt/mess.txt')
        invited_list = []

        while total_count < 2000:
            while True:
                users_ids_list = []
                cookies_list = []

                page_range = self._get_pages_range()

                for page in page_range:
                    json_data = self._get_chat_page(page=page)
                    if json_data['result'] == 'ok' and type(json_data['online']) == dict:
                        for key, user in json_data['online'].items():
                            if str(user['id']) not in invited_list:
                                if str(user['id']) not in self.ignore_list:
                                    message = random.choice(messages).replace('{man_name}', user['name'].split(' ')[0].capitalize())
                                    result_send = self._send_chat_message(user['id'], message)
                                    if result_send == 'ok':
                                        users_ids_list.append(user['id'])
                                        ch += 1
                                        total_count += 1
                                    time.sleep(self.DELAY)
                                else:
                                    self.log(str(user['id']) + ' in ignore list')
                            else:
                                self.log(str(user['id']) + ' already invited (invited list)')
                    try:
                        cookies_list.extend(self.session.cookies['invited_list'].split('%2C'))
                    except KeyError:
                        print('No COOKIE')

                    invited_list.extend(cookies_list)
                    invited_list = list(set(invited_list))
                    cookies_list.clear()

                    print('Page invited: ' + str(page) + ', invited users: ' + str(ch))
                    ch = 0
                print('Invites sent: ', len(users_ids_list))
                if len(users_ids_list) <= 5:
                    invited_list.clear()
                    self.session.cookies.clear(domain='romancecompass.com', path='/chat', name='invited_list')
            print('Sleeping 10 minutes... zZzZzz...')
            print(total_count)
            time.sleep(10*60)

    def save_invited(self, filename, user_id_list):
        with open(filename, 'w') as file:
            # так можно?
            [file.write('%s\n' % user_id) for user_id in user_id_list]
        file.close()

    def log(self, data):
        file = open('./txt/log.txt', 'a')
        file.write('%s\n' % data)
        file.close()

    def load_data(self, filename):
        with open(filename, 'r') as file:
            data_list = [line.strip() for line in file]
        file.close()
        return data_list

    def clear_file(self, filename):
        file = open(filename, 'w')
        file.close()

if __name__ == '__main__':
    pass