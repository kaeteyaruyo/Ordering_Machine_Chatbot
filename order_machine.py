from transitions.extensions import GraphMachine

class OrderingMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(
            model=self,
            **machine_configs
        )
        self.order_list = []
        self.customer_info = ""
        while not len(input('Enter anything to start: ')) > 0:
            pass
        else:
            self.start()

    def on_enter_options(self, event):
        print('CURRENT STATE: ' + self.state)
        print("What can I do for you?\n* Order\n* Menu\n* Contact us")
        self.choose_service(text = input())

    def on_enter_order_drink(self, event):
        print('CURRENT STATE: ' + self.state)
        drink = input('What would you like to drink? (Enter one drink per input)\n')
        self.order_list.append({'drink': drink})
        self.to_sugar()

    def on_enter_order_sugar(self, event):
        print('CURRENT STATE: ' + self.state)
        sugar = input('Which sweetness level would you like?\n* Regular sugar\n* Less sugar\n* Half sugar\n* Quarter sugar\n* Sugar-free\n')
        self.order_list[-1]['sugar'] = sugar
        self.to_ice()

    def on_enter_order_ice(self, event):
        print('CURRENT STATE: ' + self.state)
        ice = input('How much ice would you like?\n* Regular ice\n* Easy ice\n* Ice-free\n* Hot\n')
        self.order_list[-1]['ice'] = ice
        self.to_topping()

    def on_enter_order_topping(self, event):
        print('CURRENT STATE: ' + self.state)
        topping = input('Any topping?\n* Adzuki bean\n* Lemon\n* Tapioka(Big)\n* Tapioka(Small)\n* No, Thanks\n')
        self.order_list[-1]['topping'] = topping if not topping == 'No, Thanks' else None
        self.check_order()

    def on_enter_order_check(self, event):
        print('CURRENT STATE: ' + self.state)
        print('Please check your order:')
        print(self.order_list)
        print('* Continue order\n* Delete order\n* Finish order\n')
        self.choose_order_action(text = input())

    def on_enter_order_delete(self, event):
        print('CURRENT STATE: ' + self.state)
        print('Which drink would you want to delete? (Enter number)')
        for i in range(len(self.order_list)):
            print(f'[{i + 1}] { self.order_list[i]["drink"] }')
        num = int(input())
        del self.order_list[num - 1]
        self.check_order()

    def on_enter_order_delivery(self, event):
        print('CURRENT STATE: ' + self.state)
        print('Which way would you take your drinks?\n* Take away\n* Delivery\n')
        self.choose_delivery_way(text = input())

    def on_enter_order_info(self, event):
        print('CURRENT STATE: ' + self.state)
        print('Please provide your name, address and phone number:\n')
        self.customer_info = input()
        self.finish_order()

    def on_enter_order_finish(self, event):
        print('CURRENT STATE: ' + self.state)
        print('Thanks for your purchase!\n')
        self.start()

    def on_enter_menu(self, event):
        print('CURRENT STATE: ' + self.state)
        self.start()

    def on_enter_contact(self, event):
        print('CURRENT STATE: ' + self.state)
        self.start()

    def making_order(self, event):
        return event.kwargs.get('text') == 'Order'

    def requesting_menu(self, event):
        return event.kwargs.get('text') == 'Menu'

    def contacting(self, event):
        return event.kwargs.get('text') == 'Contact us'

    def continuing_order(self, event):
        return event.kwargs.get('text') == 'Continue order'

    def deleting_order(self, event):
        return event.kwargs.get('text') == 'Delete order'

    def finishing_order(self, event):
        return event.kwargs.get('text') == 'Finish order'

    def choosing_takeaway(self, event):
        return event.kwargs.get('text') == 'Take away'

    def choosing_delivery(self, event):
        return event.kwargs.get('text') == 'Delivery'

if __name__ == "__main__":
    machine = OrderingMachine(
        states=[
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
            'contact',
        ],
        transitions=[
            {
                'trigger': 'start',
                'source': ['init', 'menu', 'contact', 'order_finish'],
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
                'dest': 'contact',
                'conditions': 'contacting'
            },
            {
                'trigger': 'choose_service',
                'source': 'options',
                'dest': 'event',
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
        initial='init',
        auto_transitions=False,
        show_conditions=True,
        send_event=True,
    )