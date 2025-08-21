from firebase_functions import https_fn, options


@https_fn.on_request(
	cors=options.CorsOptions(
		cors_origins=["*"],
		cors_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
	)
)
def django_app(req: https_fn.Request) -> https_fn.Response:
	return https_fn.Response("OK", status=200, headers={"Content-Type": "text/plain; charset=utf-8"})
