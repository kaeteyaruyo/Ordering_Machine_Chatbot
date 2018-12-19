from transitions.extensions import GraphMachine
from utils import send_text, send_image_url, send_postback_button, send_quick_reply, send_url_button
from database import get_popular_drink, get_drink_info, get_sweetness, get_ice, get_topping, update_sale_count

class OrderingMachine(GraphMachine):
    def __init__(self, session_id):
        self.machine = GraphMachine(
            model = self,
            states = [
                'init',
                'options',
                'order_drink',
                'order_sugar',
                'order_ice',
                'order_topping',
                'order_check',
                'order_delete',
                'order_delivery',
                'order_info',
                'order_finish',
                'menu',
                'sale_event',
                'error',
            ],
            transitions = [
                {
                    'trigger': 'to_option',
                    'source': ['init', 'menu', 'sale_event', 'order_finish'],
                    'dest': 'options',
                },
                {
                    'trigger': 'choose_service',
                    'source': 'options',
                    'dest': 'order_drink',
                    'conditions': 'service_order'
                },
                {
                    'trigger': 'choose_service',
                    'source': 'options',
                    'dest': 'menu',
                    'conditions': 'service_menu'
                },
                {
                    'trigger': 'choose_service',
                    'source': 'options',
                    'dest': 'sale_event',
                    'conditions': 'service_event'
                },
                {
                    'trigger': 'to_order_sugar',
                    'source': 'order_drink',
                    'dest': 'order_sugar',
                },
                {
                    'trigger': 'to_order_ice',
                    'source': 'order_sugar',
                    'dest': 'order_ice',
                },
                {
                    'trigger': 'to_order_topping',
                    'source': 'order_ice',
                    'dest': 'order_topping',
                },
                {
                    'trigger': 'to_order_check',
                    'source': ['order_topping', 'order_delete'],
                    'dest': 'order_check',
                },
                {
                    'trigger': 'choose_order_action',
                    'source': 'order_check',
                    'dest': 'order_drink',
                    'conditions': 'order_continue'
                },
                {
                    'trigger': 'choose_order_action',
                    'source': 'order_check',
                    'dest': 'order_delete',
                    'conditions': 'order_delete'
                },
                {
                    'trigger': 'choose_order_action',
                    'source': 'order_check',
                    'dest': 'order_delivery',
                    'conditions': 'order_finish'
                },
                {
                    'trigger': 'choose_delivery_way',
                    'source': 'order_delivery',
                    'dest': 'order_finish',
                    'conditions': 'deliver_takeaway'
                },
                {
                    'trigger': 'choose_delivery_way',
                    'source': 'order_delivery',
                    'dest': 'order_info',
                    'conditions': 'deliver_delivery'
                },
                {
                    'trigger': 'to_order_finish',
                    'source': 'order_info',
                    'dest': 'order_finish',
                },
                {
                    'trigger': 'to_error',
                    'source': ['order_drink', 'order_sugar', 'order_ice', 'order_topping', 'order_delivery'],
                    'dest': 'error',
                },
                {
                    'trigger': 'return_from_error',
                    'source': 'error',
                    'dest': 'order_drink',
                    'conditions': 'error_drink'
                },
                {
                    'trigger': 'return_from_error',
                    'source': 'error',
                    'dest': 'order_sugar',
                    'conditions': 'error_sugar'
                },
                {
                    'trigger': 'return_from_error',
                    'source': 'error',
                    'dest': 'order_ice',
                    'conditions': 'error_ice'
                },
                {
                    'trigger': 'return_from_error',
                    'source': 'error',
                    'dest': 'order_topping',
                    'conditions': 'error_topping'
                },
                {
                    'trigger': 'return_from_error',
                    'source': 'error',
                    'dest': 'order_delivery',
                    'conditions': 'error_delivery'
                },
            ],
            initial = 'init',
            auto_transitions = False,
            show_conditions = True,
            send_event = True,
        )
        self.id = session_id
        self.order_list = []
        self.customer_info = ""
        self.to_option()

    def transit(self, event):
        if self.state == 'options':
            if 'postback' in event:
                self.choose_service(service = event['postback']['payload'])
        elif self.state == 'order_drink':
            try:
                drink_info = get_drink_info(event['message']['text'])
            except KeyError:
                self.to_error(error = 'ERROR_DRINK')
            else:
                if not drink_info == None:
                    self.order_list.append({'name': event['message']['text']})
                    self.order_list[-1]['id'] = drink_info[0]
                    self.order_list[-1]['price'] = drink_info[1]
                    self.to_order_sugar()
                else:
                    self.to_error(error = 'ERROR_DRINK')
        elif self.state == 'order_sugar':
            try:
                self.order_list[-1]['sugar'] = event['message']['quick_reply']['payload']
            except KeyError:
                self.to_error(error = 'ERROR_SUGAR')
            else:
                self.to_order_ice()
        elif self.state == 'order_ice':
            try:
                self.order_list[-1]['ice'] = event['message']['quick_reply']['payload']
            except KeyError:
                self.to_error(error = 'ERROR_ICE')
            else:
                self.to_order_topping()
        elif self.state == 'order_topping':
            try:
                topping = event['message']['quick_reply']['payload']
            except KeyError:
                self.to_error(error = 'ERROR_TOPPING')
            else:
                if not topping == 'None':
                    name, price = topping.split(' ')
                    self.order_list[-1]['topping'] = name
                    self.order_list[-1]['price'] += int(price)
                self.to_order_check()
        elif self.state == 'order_check':
            try:
                self.choose_order_action(action = event['message']['quick_reply']['payload'])
            except KeyError:
                send_quick_reply(self.id, '是否要繼續點餐？（請選擇以下按鈕）', [
                    {
                        'text': '繼續點餐',
                        'value': 'ORDER_CONTINUE',
                    },
                    {
                        'text': '修改餐點',
                        'value': 'ORDER_DELETE',
                    },
                    {
                        'text': '完成點餐',
                        'value': 'ORDER_FINISH',
                    },
                ])
        elif self.state == 'order_delete':
            try:
                num = int(event['message']['text']) - 1
            except KeyError:
                send_text(self.id, '請輸入餐點編號')
            except ValueError:
                send_text(self.id, '請輸入餐點編號')
            else:
                if num < -1 or num >= len(self.order_list):
                   send_text(self.id, '請輸入餐點編號')
                else:
                    if not num == -1:
                        del self.order_list[num]
                    self.to_order_check()
        elif self.state == 'order_delivery':
            try:
                self.choose_delivery_way(way = event['message']['quick_reply']['payload'])
            except KeyError:
                self.to_error(error = 'ERROR_DELIVERY')
        elif self.state == 'order_info':
            try:
                self.customer_info = event['message']['text']
            except KeyError:
                send_text(self.id, '請輸入您的姓名、聯絡電話與地址')
            else:
                self.to_order_finish()
        elif self.state == 'order_finish':
            self.to_option()

    def on_enter_options(self, event):
        send_postback_button(self.id, '歡迎光臨茶湯會！請問您需要什麼服務呢？', [
            {
                'text': '點餐',
                'value': 'SERVICE_ORDER',
            },
            {
                'text': '看菜單',
                'value': 'SERVICE_MENU',
            },
            {
                'text': '優惠活動',
                'value': 'SERVICE_EVENT',
            },
        ])

    def on_enter_order_drink(self, event):
        send_quick_reply(self.id, '請問您想喝什麼？（請一次輸入一種飲料）', [
            {
                'text': drink,
                'value': drink,
            }
            for drink in get_popular_drink()
        ])

    def on_enter_order_sugar(self, event):
        send_quick_reply(self.id, '請選擇甜度（請選擇以下按鈕）', [
            {
                'text': sweetness,
                'value': sweetness,
            }
            for sweetness in get_sweetness(self.order_list[-1]['id'])
        ])

    def on_enter_order_ice(self, event):
        send_quick_reply(self.id, '請選擇冰量（請選擇以下按鈕）', [
            {
                'text': ice,
                'value': ice,
            }
            for ice in get_ice(self.order_list[-1]['id'])
        ])

    def on_enter_order_topping(self, event):
        send_quick_reply(self.id, '請問需要其它加料嗎？（請選擇以下按鈕）', [
            *(
                {
                    'text': f'{ topping[0] }（加{ topping[1] }元）',
                    'value': f'{ topping[0] } { topping[1] }'
                }
                for topping in get_topping()
            ),
            {
                'text': '不用，謝謝',
                'value': 'None',
            }
        ])

    def on_enter_order_check(self, event):
        send_text(self.id, '請確認您的餐點:')
        send_text(self.id, '\n'.join(self.order_list_tostring()))
        send_quick_reply(self.id, '是否要繼續點餐？（請選擇以下按鈕）', [
            {
                'text': '繼續點餐',
                'value': 'ORDER_CONTINUE',
            },
            {
                'text': '修改餐點',
                'value': 'ORDER_DELETE',
            },
            {
                'text': '完成點餐',
                'value': 'ORDER_FINISH',
            },
        ])

    def on_enter_order_delete(self, event):
        send_text(self.id, '請問要刪除哪一筆餐點呢？（請輸入編號，若無欲刪除餐點請輸入0）:')
        send_text(self.id, '\n'.join(self.order_list_tostring()))

    def on_enter_order_delivery(self, event):
        send_quick_reply(self.id, '請問您要外帶還是外送？（請選擇以下按鈕）', [
            {
                'text': '外帶',
                'value': 'DELIVER_TAKEAWAY',
            },
            {
                'text': '外送',
                'value': 'DELIVER_DELIVERY',
            },
        ])

    def on_enter_order_info(self, event):
        send_text(self.id, '請輸入您的姓名、聯絡電話與地址')

    def on_enter_order_finish(self, event):
        update_sale_count(self.order_list)
        send_text(self.id, '已收到您的訂單，感謝您的惠顧！')
        send_text(self.id, '如須其它服務，請傳送任意訊息~')

    def on_exit_order_finish(self, event):
        self.order_list = []

    def on_enter_error(self, event):
        error = event.kwargs.get('error')
        if error == 'ERROR_DRINK':
            send_text(self.id, '很抱歉，我們目前沒有提供這項飲品')
        elif error == 'ERROR_SUGAR':
            send_text(self.id, '很抱歉，這項飲品沒有提供這個甜度選項')
        elif error == 'ERROR_ICE':
            send_text(self.id, '很抱歉，這項飲品沒有提供這個冰量選項')
        elif error == 'ERROR_TOPPING':
            send_text(self.id, '很抱歉，我們目前沒有提供這項配料')
        elif error == 'ERROR_DELIVERY':
            send_text(self.id, '請從按鈕選擇領取方式')
        self.return_from_error(error = error)

    def on_enter_menu(self, event):
        send_url_button(self.id, '請參考官網~', [
            {
                'text': '茶湯會2018冬季菜單',
                'url': 'https://tw.tp-tea.com/menu/index.php?index_m1_id=17',
            }
        ])
        self.to_option()

    def on_enter_sale_event(self, event):
        send_text(self.id,
        """
【 購物節與 momo 特別企劃 】
→ https://momo.dm/E3rNy7
冬季飲品 #多項優惠任你轉
黑五沒跟到沒關係，雙12肯定還是要搶購一波！
幸運輪盤轉一轉，就有機會轉到 #堅果品項免費招待券
憑電子兌換券到門店，即可體驗堅果新品
快分享給你的朋友，有空來喝茶～
　
│秉持堅持分享原則，好康share with u│
幸福茶，如何轉入門
點入活動連結，登入momo會員。
舊會員可轉1次轉盤，新會員可轉2次！
並到門市換購飲料，請出示電子優惠券畫面，請店員協助兌換。
　
#詳細活動辦法詳見連結
#活動不與其他優惠併用
#百貨商場門市恕不適用
#單筆消費限兌一份優惠
        """)
        send_image_url(self.id, 'https://tw.tp-tea.com/upload/news_b/2163313f4e8eab9a37153c006d7ca245.jpg')
        self.to_option()

    def service_order(self, event):
        return event.kwargs.get('service') == 'SERVICE_ORDER'

    def service_menu(self, event):
        return event.kwargs.get('service') == 'SERVICE_MENU'

    def service_event(self, event):
        return event.kwargs.get('service') == 'SERVICE_EVENT'

    def order_continue(self, event):
        return event.kwargs.get('action') == 'ORDER_CONTINUE'

    def order_delete(self, event):
        return event.kwargs.get('action') == 'ORDER_DELETE'

    def order_finish(self, event):
        return event.kwargs.get('action') == 'ORDER_FINISH'

    def deliver_takeaway(self, event):
        return event.kwargs.get('way') == 'DELIVER_TAKEAWAY'

    def deliver_delivery(self, event):
        return event.kwargs.get('way') == 'DELIVER_DELIVERY'

    def error_drink(self, event):
        return event.kwargs.get('error') == 'ERROR_DRINK'

    def error_sugar(self, event):
        return event.kwargs.get('error') == 'ERROR_SUGAR'

    def error_ice(self, event):
        return event.kwargs.get('error') == 'ERROR_ICE'

    def error_topping(self, event):
        return event.kwargs.get('error') == 'ERROR_TOPPING'

    def error_delivery(self, event):
        return event.kwargs.get('error') == 'ERROR_DELIVERY'

    def order_list_tostring(self):
        string = [
            f"[{ idx + 1 }] { order['name'] } { order['sugar'] }{ order['ice'] } { '加' + order['topping'] if 'topping' in order else '' } { order['price'] }元"
            for idx, order in enumerate(self.order_list)
        ]
        string.append(f'總共是{ sum(order["price"] for order in self.order_list ) }元')
        return string