import json
import copy
from http.server import BaseHTTPRequestHandler, HTTPServer

DATABASE = {
    "METALS": [
        {"id": 1, "metal": "Sterling Silver", "price": 12.42},
        {"id": 2, "metal": "14K Gold", "price": 736.4},
        {"id": 3, "metal": "24K Gold", "price": 1258.9},
        {"id": 4, "metal": "Platinum", "price": 795.45},
        {"id": 5, "metal": "Palladium", "price": 1241.0}
    ],
    "STYLES": [
        {"id": 1, "style": "Classic", "price": 500},
        {"id": 2, "style": "Modern", "price": 710},
        {"id": 3, "style": "Vintage", "price": 965}
    ],
    "TYPES": [
        {"id": 1,"name": "Earring"},
        {"id": 2,"name": "Ring"},
        {"id": 3,"name": "Necklace"}
        ],
    "SIZES": [
        {"id": 1, "carets": 0.5, "price": 405},
        {"id": 2, "carets": 0.75, "price": 782},
        {"id": 3, "carets": 1, "price": 1470},
        {"id": 4, "carets": 1.5, "price": 1997},
        {"id": 5, "carets": 2, "price": 3638}
    ],
    "ORDERS": [
        {
            "id": 1,
            "metalId": 3,
            "sizeId": 2,
            "styleId": 3,
            "timestamp": "2018-01-01 12:01:01",
            "jewelryTypeId": 3
        }]}

def single(resource, id):
    """For GET requests to single resource"""
    response = None
    for element in DATABASE[resource.upper()]:
        if element["id"] == id:
            response = element
    return response

def all(resource):
    """For GET requests to collection"""
    if resource == 'orders':
        data = DATABASE[resource.upper()][:]
        new_data = copy.deepcopy(data)
        for order in new_data:
            order["metal"] = single("METALS", order["metalId"])
            order["size"] = single("SIZES", order["sizeId"])
            order["style"] = single("STYLES", order["styleId"])
            order["type"] = single("TYPES", order["jewelryTypeId"])
            del order["metalId"], order["sizeId"], order["styleId"], order["jewelryTypeId"]
        return new_data
    else:
        return DATABASE[resource.upper()]

def create(resource, new_item):
    max_id = DATABASE[resource.upper()][-1]["id"]
    new_id = max_id + 1
    new_item["id"] = new_id
    DATABASE[resource.upper()].append(new_item)
    return new_item

def delete(resource, id):
    """For DELETE requests"""
    element_index = -1
    for index, element in enumerate(DATABASE[resource.upper()]):
        if element["id"] == id:
            element_index = index
    if element_index >= 0:
        DATABASE[resource.upper()].pop(element_index)
    pass

def update(resource, id, new_item):
    """For PUT requests"""
    for index, element in enumerate(DATABASE[resource.upper()]):
        if element["id"] == id:
            DATABASE[resource.upper()][index] = new_item
            break

class HandleRequests(BaseHTTPRequestHandler):
    """Controls the functionality of any GET, PUT, POST, DELETE requests to the server
    """

    def parse_url(self, path):
        path_params = path.split("/")
        resource = path_params[1]
        id = None
        try:
            id = int(path_params[2])
        except IndexError:
            pass
        except ValueError:
            pass
        return (resource, id)

    def get_all_or_single(self, resource, id):
        if id is not None:
            response = single(resource, id)
            if response is not None:
                self._set_headers(200)
            else:
                self._set_headers(404)
                response = {"error": "Not Found"}
        else:
            self._set_headers(200)
            response = all(resource)
        return response

    def do_GET(self):
        response = None
        (resource, id) = self.parse_url(self.path)
        response = self.get_all_or_single(resource, id)
        if response is None:
            self._set_headers(404)
            response = {"error": "Not Found"}
        self.wfile.write(json.dumps(response).encode())

    def _set_headers(self, status):
        """Sets the status code, Content-Type and Access-Control-Allow-Origin
        headers on the response
        Args:
            status (number): the status code to return to the front end
        """
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_POST(self):
        content_len = int(self.headers.get('content-length', 0))
        post_body = self.rfile.read(content_len)
        post_body = json.loads(post_body)
        (resource, id) = self.parse_url(self.path)
        new_post = None
        if resource == "orders":
            if "metalId" in post_body and "jewelryTypeId" in post_body and "sizeId" in post_body and "styleId" in post_body:
                self._set_headers(201)
                new_post = create(resource, post_body)
            else:
                self._set_headers(400)
                new_post = {
                    "message": f'{"metal is required" if "metal" not in post_body else ""} {"jewelryType is required" if "jewelryType" not in post_body else ""} {"size is required" if "size" not in post_body else ""} {"style is required" if "style" not in post_body else ""}'
                }
        if resource != "orders":
            self._set_headers(405)
            new_post = {"error": "not allowed"}
        self.wfile.write(json.dumps(new_post).encode())

    def do_DELETE(self):
        self._set_headers(204)
        (resource, id) = self.parse_url(self.path)
        if resource == "orders":
            response = {"message": "success"}
        self.wfile.write(json.dumps(response).encode())

    def do_PUT(self):
        content_len = int(self.headers.get('content-length', 0))
        post_body = self.rfile.read(content_len)
        post_body = json.loads(post_body)
        (resource, id) = self.parse_url(self.path)
        if resource == 'metals':
            self._set_headers(201)
            response = {"message": "success"}
        else:
            self._set_headers(400)
            response = {"error": "not allowed"}
        self.wfile.write(json.dumps(response).encode())

def main():
    """Starts the server on port 8088 using the HandleRequests class
    """
    host = ''
    port = 8088
    HTTPServer((host, port), HandleRequests).serve_forever()


if __name__ == "__main__":
    main()
