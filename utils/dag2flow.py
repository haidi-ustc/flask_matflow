import hashlib
import copy
import json
import numpy  as  np
import networkx as nx
from enum import Enum
from jsonschema import validate, ValidationError
from pydantic import BaseModel
from typing import List, Dict, Union, IO
from monty.serialization import loadfn, dumpfn
from monty.json import MSONable

# relative import for flask project
from utils.utils import jsanitize


class Dag2Flow(MSONable):
    def __init__(self, input_data: Union[str, Dict], include_hash=False, start_id="666", end_id="888"):
        """
        Constructs a Dag2Flow object from either a file object or a dictionary.

        Args:
            input_data (Union[str, Dict]): Either the name of the JSON file containing
                the DAG data (str) or a dictionary representing the DAG.
            include_hash (bool, optional): Whether to include the hash code
            in the node label IDs. Defaults to True.
            start_id (str): The ID of the start node in the DAG.
            end_id (str): The ID of the end node in the DAG.

        Raises:
            AssertionError: If the 'nodes' or 'edges' keys are not present in
                the JSON data (if input_data is a dictionary), or if there is a problem
                with the start and end nodes in the DAG.
        """
        if isinstance(input_data, str):  # Input is a file path
            self.filename = input_data
            self.workflow_data = self._load_workflow_data(input_data)
        elif isinstance(input_data, dict):  # Input is a dictionary
            self.filename = None  # No filename in this case
            self.workflow_data = input_data
            # Validate the input data (optional, if needed)
            #validate(instance=input_data, schema=schema)
        else:
            raise ValueError("Invalid input_data type. Expected str or dict.")

        self.nodes_data = self.workflow_data["nodes"]
        self.nodes = self._get_nodes()
        self.edges = self.workflow_data["edges"]
        self.include_hash = include_hash
        if self.include_hash:
            self._set_hash()
        else:
            self._json_hash = None
        self.start_id = start_id
        self.end_id = end_id
        self._check_integrity()
        self.dag = nx.DiGraph()
        self._set_dag()

    def _load_workflow_data(self, filename):
        try:
            workflow_data = loadfn(filename)
            # Validate JSON schema if available (replace with your schema)
            #validate(instance=workflow_data, schema=schema)
            return workflow_data
        except (FileNotFoundError, json.JSONDecodeError, ValidationError) as e:
            raise RuntimeError(f"Error loading JSON file: {e}")

    @classmethod
    def from_dict(cls, d):
        """
        Construct a Dag2Flow object from a dictionary.
    
        Args:
            d (dict): A dictionary representing a Dag2Flow object.
    
        Returns:
            Dag2Flow: An instance of the Dag2Flow class.
        """
        input_data = d["input_data"]
        start_id = d["start_id"]
        end_id = d["end_id"]
    
        # Infer include_hash based on the presence of _json_hash
        include_hash = "_json_hash" in d
    
        return cls(input_data, include_hash, start_id, end_id)
    
    def as_dict(self):
        """
        Serialize the Dag2Flow object to a dictionary.
    
        Returns:
            dict: A dictionary representation of the Dag2Flow object.
        """
        data = {
            "@module": self.__class__.__module__,
            "@class": self.__class__.__name__,
            "input_data": self.workflow_data if self.workflow_data else self.filename,
            "start_id": self.start_id,
            "end_id": self.end_id
        }
    
        if self.include_hash:
            data["_json_hash"] = self._json_hash
    
        return data


    def _set_dag(self):
        """Constructs a `networkx.DiGraph` object representing the DAG."""
        for edge in self.edges:
            src_label_id = self.get_node_label_id(edge["src_node_id"])
            dst_label_id = self.get_node_label_id(edge["dst_node_id"])
            self.dag.add_edge(src_label_id, dst_label_id)

    def plot_dag(self, filename="workflow.png"):
        """Plots the DAG and saves the plot to a file.

        Args:
            filename (str): The name of the file to save the plot to.

        """
        import matplotlib
        matplotlib.use('agg')
        import matplotlib.pyplot as plt
        nx.draw_networkx(self.dag)
        plt.savefig(filename)

    def _check_integrity(self):
        """Checks that the DAG has at least one start node and one end node.

        Raises:
            AssertionError: If there is a problem with the start and end nodes
                in the DAG.

        """
        start_nodes = []
        end_nodes = []
        for node in self.nodes_data:
            if self.start_id in node["id"]:
                start_nodes.append(node)
            if self.end_id in node["id"]:
                end_nodes.append(node)
        assert len(start_nodes) == len(end_nodes)
        assert len(start_nodes) > 0

    def _get_nodes(self):
        """Constructs a dictionary that maps node IDs to node dictionaries."""
        nodes = {}
        for node in self.nodes_data:
            nodes[node["id"]] = node
        return nodes

    def get_node_type(self, node_id):
        """Returns the type for a given node ID.
    
        Args:
            node_id (str): The ID of the node.
    
        Returns:
            str: The type of the node.
    
        """
        node = self.nodes[node_id]
        return node["type"]

    def get_node_label(self, node_id):
        """Returns the label for a given node ID.
    
        Args:
            node_id (str): The ID of the node.
    
        Returns:
            str: The label of the node.
    
        """
        node = self.nodes[node_id]
        return node["label"]
    
    def get_node_meta(self, node_id):
        """Returns the metadata for a given node ID.
    
        Args:
            node_id (str): The ID of the node.
    
        Returns:
            Any: The metadata of the node.
    
        """
        node = self.nodes[node_id]
        return node["meta"]
    
    def _set_hash(self):
        json_data = json.dumps(self.workflow_data, sort_keys=True).encode()
        hash_object = hashlib.sha256(json_data)
        self._json_hash = hash_object.hexdigest()[:16]

    def get_node_label_id(self, node_id):
        """Returns a string that combines the node's label, ID, and hash code for
        the entire JSON file.
    
        Args:
            node_id (str): The ID of the node.
    
        Returns:
            str: A string that combines the node's label, ID, and hash code for
                the entire JSON file.
    
        """
        node = self.nodes[node_id]
        return f"{node['label']}_{node['id']}"
  
    def get_nodes_event(self):
        """Returns a string that defines a `DummyTask` or `PythonTask` for each
        node in the DAG.
    
        Returns:
            str: A string that defines a `DummyTask` or `PythonTask` for each
                node in the DAG.
    
        """
        rets = ""
        for node in self.nodes_data:
            rets += self.get_node_event(node["id"])
        return rets
    
    def get_node_event(self, node_id):
        """Returns a string that defines a `DummyTask` or `VaspTask` for a
        given node ID.
    
        Args:
            node_id (str): The ID of the node.
    
        Returns:
            str: A string that defines a `DummyTask` or `VaspTask` for the
                node.
    
        """
        label_id = self.get_node_label_id(node_id)
        node_type = self.get_node_type(node_id)
        meta = self.get_node_meta(node_id)
    
        if self.start_id in node_id:
            return "##" * 40 + f"\n{label_id}=InitializeTask(name='{label_id}',filename=filename.replace('.py','.json'))\n\n"
        if self.end_id in node_id:
            #node_id_parts = node_id.split("_")
            #node_id_parts[0] = "finalize"
            #node_name = "_".join(node_id_parts)
            return "##" * 40 + f"\n{label_id}=FinalizeTask(name='{label_id}')\n\n"

        if 'vasp' in node_type:
    
            return "##" * 40 + f"""\n{label_id}=VaspTask(
                   name="{label_id}",
                   calculation_type="{node_type}",
                   callback=None,
                   task_args={meta}
                   )\n\n"""

        if 'database' in node_type:
    
            return "##" * 40 + f"""\n{label_id}=DatabaseTask(
                   name="{label_id}",
                   callback=None,
                   task_args={meta}
                   )\n\n"""


    def get_airflow_dependencies(self):
        """Returns a list of strings that define the dependencies between tasks
        in the DAG, using `set_downstream()`.
    
        Returns:
            List[str]: A list of strings that define the dependencies between
                tasks in the DAG.
    
        """
        rets = []
        for edge in self.edges:
            src_label_id = self.get_node_label_id(edge["src_node_id"])
            dst_label_id = self.get_node_label_id(edge["dst_node_id"])
            rets.append(f"{src_label_id}.set_downstream({dst_label_id})")
        return rets
    
    def get_dependencies(self):
        """Returns a list of strings that define the dependencies between tasks
        in the DAG.
    
        Returns:
            Dict[str]: A list of strings that define the dependencies between
                tasks in the DAG.
    
        """
        dependencies = {}
        for edge in self.edges:
            src_label_id = self.get_node_label_id(edge["src_node_id"])
            dst_label_id = self.get_node_label_id(edge["dst_node_id"])
            if src_label_id not in dependencies:
                dependencies[src_label_id] = [dst_label_id]
            else:
                dependencies[src_label_id].append(dst_label_id)
        return dependencies
    
    def get_lightflow_dependencies(self):
        """Returns a list of strings that define the dependencies between tasks
        in the DAG.
    
        Returns:
            List[str]: A list of strings that define the dependencies between
                tasks in the DAG.
    
        """
        dependencies = self.get_dependencies()
        dependencies_new = copy.deepcopy(dependencies)
        for key in dependencies.keys():
            if len(dependencies[key]) == 1:
                dependencies_new[key] = dependencies[key][0]
        dag_name = self._json_hash if self.include_hash else "main_dag"
        define_items = []
        for key, val in dependencies_new.items():
            if isinstance(val, list):
                val_str = "[" + ", ".join([f'{v}' for v in val]) + "]"
            else:
                val_str = f'{val}'
            define_items.append(f"{key}: {val_str}")
        define_str = ", ".join(define_items)
        return [f"d=Dag('{dag_name}')\nd.define({{{define_str}}})"] 

    @classmethod
    def get_script(cls, input_data, workflow='lightflow', output_file='output.py', **kwargs):
        """
        Returns a single string that defines the workflow tasks and their dependencies
        based on the DAG created by the Dag2Flow object, and also defines each node
        in the workflow as a task.

        Args:
            input_data (Union[str, Dict]): Either the name of the JSON file containing
            workflow (str): The workflow platform to generate the script for.
                            Either 'lightflow' or 'airflow'.
            output_file (str): The name of the file to write the output to.
            **kwargs: Additional keyword arguments to pass to the Dag2Flow constructor.

        Returns:
            str: A string that defines the workflow tasks and their dependencies, and
                 also defines each node in the workflow as a task.

        """
        prefix="""import os
import time
from lightflow.logger import get_logger
from lightflow.models import Dag, DataStoreDocumentSection
from lightflow.models.task_data import TaskData,MultiTaskData
from lightflow.models.action import Action
from lightflow.models.parameters import Parameters,Option
from lightflow.tasks.document import RunningDocument
from lightflow.tasks import InitializeTask, FinalizeTask, VaspTask, DatabaseTask

logger = get_logger(__name__)

parameters=Parameters([
              Option('TaskDocument',RunningDocument().dict(),type=dict),
              Option('Dag',{},type=dict)
             ])

filename = os.path.basename(__file__)
print(filename)

"""
        wf = cls(input_data, **kwargs)
        if workflow == 'lightflow':
            script = prefix+wf.get_nodes_event() + "\n" + "\n".join(wf.get_lightflow_dependencies())
        elif workflow == 'airflow':
            script = wf.get_nodes_event() + "\n" + "\n".join(wf.get_airflow_dependencies())
        else:
            raise RuntimeError('Unsupported workflow platform: {}'.format(workflow))

        output_file = wf._json_hash+'.py' if wf._json_hash else output_file
        dumpfn(wf.as_dict(),output_file.replace('.py','.json'))
        if output_file is not None:
            with open(output_file, 'w') as f:
                f.write(script)

        return script

def main():
    Dag2Flow.get_script('workflow.json',include_hash=True) 
        
if __name__ == "__main__":
    script=Dag2Flow.get_script('../assets/workflow.json',include_hash=True) 
    print(script)

