import json, random, sys, logging
from urllib import request

logger: logging.Logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

endpoint: str = "http://127.0.0.1:8188"

class ImageGenerator:
    def __init__(self, style: str = "default"):
        # Check that ComfyUI is running
        # req = request.Request("http://127.0.0.1:8188/prompt")
        # request.urlopen(req)
        # if req.getcode() != 200: logger.critical("ComfyUI is not running.")
        self.set_style = style
        with open("/home/jin/Projects/modular/workflow/" + style + ".json", "r", encoding="utf-8") as f:
            self.workflow = f.read()

    def queue_prompt(self, prompt: str):
        p = {"prompt": prompt}
        data = json.dumps(p).encode('utf-8')
        req =  request.Request(endpoint + "/prompt", data=data)
        res = request.urlopen(req)
        if res.getcode() != 200:
            return False

        return True

    def text_to_image(self, text, id: int, style: str):
        if style != self.set_style:
            logger.info(f"Changing worflow from {self.set_style} to {style}")
            self.set_style = style
            self.workflow = None
            with open("/home/jin/Projects/modular/workflow/" + style + ".json", "r", encoding="utf-8") as f:
                self.workflow = f.read()

        prompt = json.loads(self.workflow)
        logger.info(f"prompt: {self.workflow}")

        if style == "default":
            prompt["6"]["inputs"]["text"] += text
            #set the seed for our KSampler node
            prompt["3"]["inputs"]["seed"] = random.randrange(1, 999999999999999)
            #set image name prefix
            prompt["13"]["inputs"]["filename_prefix"] = str(id)
        elif style == "anime":
            #set the text prompt for our positive CLIPTextEncode
            prompt["3"]["inputs"]["text"] += text
            #set the seed for our KSampler node
            prompt["2"]["inputs"]["seed"] = random.randrange(1, 999999999999999)
            #set image name prefix
            prompt["12"]["inputs"]["filename_prefix"] = str(id)
        
        if not self.queue_prompt(prompt):
            return False
        
        return True