from queries import get_component_links

def get_component_link_id(workflow_id, class_filter):
    component_links = get_component_links(workflow_id)
    for component_link in component_links:
        link_filter = component_link["filters"]
        if link_filter:
            if class_filter == link_filter["classes"]:
                return component_link["id"]
            
            