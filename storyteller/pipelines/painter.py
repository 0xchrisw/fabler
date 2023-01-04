        painter_device = torch.device(config.writer_device)

# self.painter = StableDiffusionPipeline.from_pretrained(
#     self.config.painter,
#     torch_dtype=torch.float16,
#     revision="fp16",
#     use_auth_token=False,
# ).to(painter_device)
# if self.config.disable_nsfw_check:
#     self.painter.safety_checker = self.safety_checker
