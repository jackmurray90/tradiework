from django.shortcuts import render
from django.views import View

class TradiesView(View):
    def get(self, request, tr):
        tradies = [
            {
                "id": 1,
                "name": "Bill Vasili",
                "trade": "Painter",
                "rate": 100,
            },
            {
                "id": 2,
                "name": "Mark Spark",
                "trade": "Electrician",
                "rate": 100,
            },
            {
                "id": 3,
                "name": "Simon Wood",
                "trade": "Carpenter",
                "rate": 100,
            },
            {
                "id": 4,
                "name": "David Pipes",
                "trade": "Plumber",
                "rate": 100,
            },
            {
                "id": 5,
                "name": "Charles Auto",
                "trade": "Auto mechanic",
                "rate": 100,
            },
        ]
        return render(request, f"tradies.html", {f"tradies": tradies})
