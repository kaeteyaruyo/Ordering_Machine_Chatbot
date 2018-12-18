from transitions.extensions import GraphMachine
from utils import send_text, send_image_url, send_postback_button, send_quick_reply, send_url_button
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
            ],
            transitions = [
                {
                    'trigger': 'start',
                    'source': ['init', 'menu', 'sale_event', 'order_finish'],
                    'dest': 'options',
                },
                {
                    'trigger': 'choose_service',
                    'source': 'options',
                    'dest': 'order_drink',
                    'conditions': 'making_order'
                },
                {
                    'trigger': 'choose_service',
                    'source': 'options',
                    'dest': 'menu',
                    'conditions': 'requesting_menu'
                },
                {
                    'trigger': 'choose_service',
                    'source': 'options',
                    'dest': 'sale_event',
                    'conditions': 'asking_event'
                },
                {
                    'trigger': 'to_sugar',
                    'source': 'order_drink',
                    'dest': 'order_sugar',
                },
                {
                    'trigger': 'to_ice',
                    'source': 'order_sugar',
                    'dest': 'order_ice',
                },
                {
                    'trigger': 'to_topping',
                    'source': 'order_ice',
                    'dest': 'order_topping',
                },
                {
                    'trigger': 'check_order',
                    'source': ['order_topping', 'order_delete'],
                    'dest': 'order_check',
                },
                {
                    'trigger': 'choose_order_action',
                    'source': 'order_check',
                    'dest': 'order_drink',
                    'conditions': 'continuing_order'
                },
                {
                    'trigger': 'choose_order_action',
                    'source': 'order_check',
                    'dest': 'order_delete',
                    'conditions': 'deleting_order'
                },
                {
                    'trigger': 'choose_order_action',
                    'source': 'order_check',
                    'dest': 'order_delivery',
                    'conditions': 'finishing_order'
                },
                {
                    'trigger': 'choose_delivery_way',
                    'source': 'order_delivery',
                    'dest': 'order_finish',
                    'conditions': 'choosing_takeaway'
                },
                {
                    'trigger': 'choose_delivery_way',
                    'source': 'order_delivery',
                    'dest': 'order_info',
                    'conditions': 'choosing_delivery'
                },
                {
                    'trigger': 'finish_order',
                    'source': 'order_info',
                    'dest': 'order_finish',
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
        self.start()

    def transit(self, event):
        if self.state == 'options':
            self.choose_service(service = event['postback']['payload'])
        elif self.state == 'order_drink':
            self.to_sugar(drink = event['message']['text'])
        elif self.state == 'order_sugar':
            self.to_ice(sugar = event['message']['text'])
        elif self.state == 'order_ice':
            self.to_topping(ice = event['message']['text'])
        elif self.state == 'order_topping':
            self.check_order(topping = event['message']['text'])
        elif self.state == 'order_check':
            self.choose_order_action(action = event['message']['quick_reply']['payload'])
        elif self.state == 'order_delete':
            self.check_order(num = event['message']['text'])
        elif self.state == 'order_delivery':
            self.choose_delivery_way(way = event['message']['quick_reply']['payload'])
        elif self.state == 'order_info':
            self.finish_order(info = event['message']['text'])

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
                'text': '觀音拿鐵',
                'value': '觀音拿鐵',
            },
            {
                'text': '珍珠紅豆拿鐵',
                'value': '珍珠紅豆拿鐵',
            },
            {
                'text': '翡翠檸檬',
                'value': '翡翠檸檬',
            },
        ])

    def on_exit_order_drink(self, event):
        self.order_list.append({'drink': event.kwargs.get('drink')})
        print(self.order_list)

    def on_enter_order_sugar(self, event):
        send_quick_reply(self.id, '請選擇甜度', [
            {
                'text': '全糖',
                'value': '全糖',
            },
            {
                'text': '少糖',
                'value': '少糖',
            },
            {
                'text': '半糖',
                'value': '半糖',
            },
            {
                'text': '微糖',
                'value': '微糖',
            },
            {
                'text': '無糖',
                'value': '無糖',
            },
        ])

    def on_exit_order_sugar(self, event):
        self.order_list[-1]['sugar'] = event.kwargs.get('sugar')
        print(self.order_list)

    def on_enter_order_ice(self, event):
        send_quick_reply(self.id, '請選擇冰量', [
            {
                'text': '多冰',
                'value': '多冰',
            },
            {
                'text': '正常冰',
                'value': '正常冰',
            },
            {
                'text': '少冰',
                'value': '少冰',
            },
            {
                'text': '去冰',
                'value': '去冰',
            },
            {
                'text': '熱飲',
                'value': '熱飲',
            },
        ])

    def on_exit_order_ice(self, event):
        self.order_list[-1]['ice'] = event.kwargs.get('ice')
        print(self.order_list)

    def on_enter_order_topping(self, event):
        send_quick_reply(self.id, '請問需要其它加料嗎？', [
            {
                'text': '紅豆',
                'value': '紅豆',
            },
            {
                'text': '珍珠',
                'value': '珍珠',
            },
            {
                'text': '波霸',
                'value': '波霸',
            },
            {
                'text': '檸檬',
                'value': '檸檬',
            },
            {
                'text': '不用，謝謝',
                'value': 'None',
            },
        ])

    def on_exit_order_topping(self, event):
        topping = event.kwargs.get('topping')
        self.order_list[-1]['topping'] = topping if not topping == '不用，謝謝' else None
        print(self.order_list)

    def on_enter_order_check(self, event):
        send_text(self.id, '請確認您的餐點:')
        send_text(self.id, '\n'.join(self.order_list_tostring()))
        send_quick_reply(self.id, '是否要繼續點餐？', [
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

    def on_exit_order_delete(self, event):
        num = int(event.kwargs.get('num'))
        if num > 0:
            del self.order_list[num - 1]

    def on_enter_order_delivery(self, event):
        send_quick_reply(self.id, '請問您要外帶還是外送？', [
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

    def on_exit_order_info(self, event):
        self.customer_info = event.kwargs.get('info')

    def on_enter_order_finish(self, event):
        send_text(self.id, '已收到您的訂單，感謝您的惠顧！')
        self.start()

    def on_enter_menu(self, event):
        send_url_button(self.id, '請參考官網~', [
            {
                'text': '茶湯會2018冬季菜單',
                'url': 'https://tw.tp-tea.com/menu/index.php?index_m1_id=17',
            }
        ])
        self.start()

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
        self.start()
    def making_order(self, event):
        return event.kwargs.get('service') == 'SERVICE_ORDER'

    def requesting_menu(self, event):
        return event.kwargs.get('service') == 'SERVICE_MENU'

    def asking_event(self, event):
        return event.kwargs.get('service') == 'SERVICE_EVENT'

    def continuing_order(self, event):
        return event.kwargs.get('action') == 'ORDER_CONTINUE'

    def deleting_order(self, event):
        return event.kwargs.get('action') == 'ORDER_DELETE'

    def finishing_order(self, event):
        return event.kwargs.get('action') == 'ORDER_FINISH'

    def choosing_takeaway(self, event):
        return event.kwargs.get('way') == 'DELIVER_TAKEAWAY'

    def choosing_delivery(self, event):
        return event.kwargs.get('way') == 'DELIVER_DELIVERY'

    def order_list_tostring(self):
        return [f"[{ idx + 1 }] { order['drink'] } { order['sugar'] }{ order['ice'] } { '加' + order['topping'] if not order['topping'] == None else '' }" for idx, order in enumerate(self.order_list)]