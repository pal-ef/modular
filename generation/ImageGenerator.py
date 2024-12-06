import json, random, sys, logging
from urllib import request

logger: logging.Logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

endpoint: str = "http://127.0.0.1:8188"

class ImageGenerator:
    def __init__(self):
        # # Check that ComfyUI is running
        # req = request.Request("http://127.0.0.1:8188/prompt")
        # request.urlopen(req)
        # if req.getcode() != 200:
        #     logger.critical("ComfyUI is not running.")

        # Load workflow from JSON
        with open("workflow.json", "r", encoding="utf-8") as f:
            self.workflow = f.read()

    def queue_prompt(self, prompt: str):
        p = {"prompt": prompt}
        data = json.dumps(p).encode('utf-8')
        req =  request.Request(endpoint + "/prompt", data=data)
        res = request.urlopen(req)
        if res.getcode() != 200:
            return False

        return True

    def text_to_image(self, text, id: int):
        prompt = json.loads(self.workflow)
        #set the text prompt for our positive CLIPTextEncode
        prompt["6"]["inputs"]["text"] = text
        #set the seed for our KSampler node
        prompt["3"]["inputs"]["seed"] = random.randrange(1, 999999)
        #set image name prefix
        prompt["13"]["inputs"]["filename_prefix"] = str(id)
        if not self.queue_prompt(prompt):
            return False
        
        return True