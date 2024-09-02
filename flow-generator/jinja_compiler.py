import yaml




yaml_names = ["transferencia","saldo"]

for yaml_name in yaml_names:

    with open(f'flows/{yaml_name}.yaml', 'r') as file:
        flow_data = yaml.safe_load(file)
        
        
    from jinja2 import Environment, FileSystemLoader

    # Load the template environment
    file_loader = FileSystemLoader('.')
    env = Environment(loader=file_loader)

    def dot_to_bracket(path):
        parts = path.split('.')
        return parts[0] + ''.join([f'["{part}"]' for part in parts[1:]])

    env.filters['dot_to_bracket'] = dot_to_bracket

    # Load the template
    template = env.get_template('flow_template.j2')

    # Render the template with your flow data
    rendered_code = template.render(flow=flow_data['flow'])

    # Optionally, write the rendered code to a .py file
    with open(f'../my_orchestrator/flows/{yaml_name}.py', 'w') as output_file:
        output_file.write(rendered_code)

    print(f"Flow  {yaml_name}  generado correctamente!")
