#!/usr/bin/python3

"""Defines the HBnB console."""
import cmd
import re
from shlex import split
from models import storage
from models.base_model import BaseModel
from models.user import User
from models.state import State
from models.city import City
from models.place import Place
from models.amenity import Amenity
from models.review import Review

def parse(arg):
    curly_braces_pattern = r"\{(.*?)\}"
    brackets_pattern = r"\[(.*?)\]"

    curly_braces_match = re.search(curly_braces_pattern, arg)
    brackets_match = re.search(brackets_pattern, arg)

    if not curly_braces_match:
        if not brackets_match:
            return [i.strip(",") for i in split(arg)]
        else:
            before_brackets = arg[:brackets_match.span()[0]]
            lexer = split(before_brackets)
            retl = [i.strip(",") for i in lexer]
            retl.append(brackets_match.group())
            return retl
    else:
        before_curly_braces = arg[:curly_braces_match.span()[0]]
        lexer = split(before_curly_braces)
        retl = [i.strip(",") for i in lexer]
        retl.append(curly_braces_match.group())
        return retl



class HBNBCommand(cmd.Cmd):
    """Defines the HolbertonBnB command interpreter.

    Attributes:
        prompt (str): The command prompt.
    """
    prompt = "(hbnb) "
    __classes = {
        "BaseModel",
        "User",
        "State",
        "City",
        "Place",
        "Amenity",
        "Review"
    }

    def do_quit(self, arg):
        """Quit command to exit the program."""
        return True


    def do_EOF(self, arg):
        """EOF signal to exit the program."""
        print("")
        return True

    def do_create(self, args):
        """ Create an object of any class"""
        try:
            if not args:
                raise SyntaxError()
            arg_list = args.split(" ")
            kw = {}
            for arg in arg_list[1:]:
                arg_splited = arg.split("=")
                arg_splited[1] = eval(arg_splited[1])
                if type(arg_splited[1]) is str:
                    arg_splited[1] = arg_splited[1].replace("_", " ").replace('"', '\\"')
                kw[arg_splited[0]] = arg_splited[1]
        except SyntaxError:
            print("** class name missing **")
        except NameError:
            print("** class doesn't exist **")
        new_instance = HBNBCommand.classes[arg_list[0]](**kw)
        new_instance.save()
        print(new_instance.id)


    def do_count(self, arg):
        """Usage: count <class> or <class>.count()
        Retrieve the number of instances of a given class."""
        argl = parse(arg)
        count = sum(1 for obj in storage.all().values() if argl[0] == obj.__class__.__name__)
        print(count)

    def default(self, arg):
        """Default behavior for cmd module when input is invalid"""
        argdict = {
            "all": self.do_all,
            "show": self.do_show,
            "destroy": self.do_destroy,
            "count": self.do_count,
            "update": self.do_update
        }

        # Regular expression to match the command format
        pattern = r"^(\w+)\.(\w+)\((.*?)\)$"
        match = re.match(pattern, arg)

        if match:
            obj_name, method_name, params = match.groups()
            if method_name in argdict:
                call = f"{obj_name} {params}"
                return argdict[method_name](call)

        print(f"*** Unknown syntax: {arg}")
        return False


    def do_show(self, arg):
        """
        Usage: show <class> <id> or <class>.show(<id>)
        Display the string representation of a class instance of a given id.
        """
        args = parse(arg)

        if not args:
            print("** class name missing **")
            return

        class_name = args[0]

        if class_name not in HBNBCommand.__classes:
            print("** class doesn't exist **")
            return

        if len(args) < 2:
            print("** instance id missing **")
            return

        instance_id = args[1].strip('"\'')

        objdict = storage.all()
        key = f"{class_name}.{instance_id}"

        if key not in objdict:
            print("** no instance found **")
        else:
            instance = objdict[key]
            print(str(instance))

    def emptyline(self):
        """Do nothing upon receiving an empty line."""
        pass

    def do_destroy(self, arg):
        """Usage: destroy <class> <id> or <class>.destroy(<id>)
        Delete a class instance of a given id."""
        argls = parse(arg)
        objdict = storage.all()
        if len(argls) == 0:
            print("** class name missing **")
        elif argls[0] not in HBNBCommand.__classes:
            print("** class doesn't exist **")
        elif len(argls) == 1:
            print("** instance id missing **")
        elif "{}.{}".format(argls[0], argls[1]) not in objdict.keys():
            print("** no instance found **")
        else:
            del objdict["{}.{}".format(argls[0], argls[1])]
            storage.save()

    def do_all(self, arg):
        """Usage: all or all <class> or <class>.all()
        Display string representations of all instances of a given class.
        If no class is specified, displays all instantiated objects."""
        argl = parse(arg)
        if argl and argl[0] not in HBNBCommand.__classes:
            print("** class doesn't exist **")
        else:
            objl = []
            if argl:
                class_name = argl[0]
                for obj in storage.all().values():
                    if obj.__class__.__name__ == class_name:
                        objl.append(obj.__str__())
            else:
                for obj in storage.all().values():
                    objl.append(obj.__str__())
            print(objl)


    def do_update(self, arg):
        """Usage: update <class> <id> <attribute_name> <attribute_value> or
       <class>.update(<id>, <attribute_name>, <attribute_value>) or
       <class>.update(<id>, <dictionary>)
        Update a class instance of a given id by adding or updating
        a given attribute key/value pair or dictionary."""
        argl = parse(arg)
        objdict = storage.all()

        if len(argl) == 0:
            print("** class name missing **")
            return False
        if argl[0] not in HBNBCommand.__classes:
            print("** class doesn't exist **")
            return False
        if len(argl) == 1:
            print("** instance id missing **")
            return False
        if "{}.{}".format(argl[0], argl[1]) not in objdict.keys():
            print("** no instance found **")
            return False
        if len(argl) == 2:
            print("** attribute name missing **")
            return False
        if len(argl) == 3:
            try:
                type(eval(argl[2])) != dict
            except NameError:
                print("** value missing **")
                return False

        if len(argl) == 4:
            obj = objdict["{}.{}".format(argl[0], argl[1])]
            if argl[2] in obj.__class__.__dict__.keys():
                valtype = type(obj.__class__.__dict__[argl[2]])
                obj.__dict__[argl[2]] = valtype(argl[3])
            else:
                obj.__dict__[argl[2]] = argl[3]
        elif type(eval(argl[2])) == dict:
            obj = objdict["{}.{}".format(argl[0], argl[1])]
            for k, v in eval(argl[2]).items():
                if (k in obj.__class__.__dict__.keys() and
                        type(obj.__class__.__dict__[k]) in {str, int, float}):
                    valtype = type(obj.__class__.__dict__[k])
                    obj.__dict__[k] = valtype(v)
                else:
                    obj.__dict__[k] = v
        storage.save()

if __name__ == '__main__':
    HBNBCommand().cmdloop()