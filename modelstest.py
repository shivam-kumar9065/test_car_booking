from vertexai.preview import generative_models

models = generative_models.list_models()
for model in models:
    print(model.name)
