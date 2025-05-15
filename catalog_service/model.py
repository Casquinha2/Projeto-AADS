class Order:
    def __init__(self, order_id, user_id, product_details):
        self.order_id = order_id
        self.user_id = user_id
        self.product_details = product_details

    def to_dict(self):
        return {'order_id': self.order_id,'user_id': self.user_id,
                'product_details': self.product_details}
