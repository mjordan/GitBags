#!/usr/bin/env python

"""
Script to demonstrate converting a Git log into a PREMIS document.
For more information, see https://github.com/mjordan/GitBags. This
script is in the public domain.

Usage: ./gitlog2premis.py /path/to/directory

/path/to/directory: The path to the directory that contains a GitBag.

Use shell redirection to save the XML file,
e.g., ./gitlog2premis.py /path/to/directory > premis.xml
"""

import sys
import os
import git
import xml.dom.minidom
import hashlib
import argparse

argparser = argparse.ArgumentParser()
argparser.add_argument("git_bag_dir", help = "The GitBag directory")
args = argparser.parse_args()

if not os.path.exists(args.git_bag_dir):
    sys.exit("Sorry, %s doesn't appear to exist." % args.git_bag_dir)

premis_ns = 'info:lc/xmlns/premis-v2'

repo = git.Repo(args.git_bag_dir)
git = repo.git
# Get a list of files in the repo.
files = repo.index.entries
repo_history = {}
for file in files:
    file_history = {}
    # Get the log entries for the current file. We use || for easy parsing later.
    file_result = git.log(file[0], reverse=True, date="iso", follow=True,
        pretty="format:%H || %an || %ae || %ad || %s") 
    # If there are multiple commits for a file, we need to split the entries into a list.
    file_result_list = file_result.split("\n")
    for commit in file_result_list:
        commit_details_preclean = commit.split("||")    
        commit_details = [value.strip() for value in commit_details_preclean]
        commit_hash = commit_details.pop(0)
        file_history[commit_hash] = commit_details
    repo_history[file[0]] = file_history

doc = xml.dom.minidom.Document()
premis_element = doc.createElementNS("info:lc/xmlns/premis-v2", "premis")
doc.appendChild(premis_element)

# We want to create an <object> element for each file.
for file in files:
    object_element = doc.createElementNS(premis_ns, "object")
    premis_element.appendChild(object_element)

    object_identifier_element = doc.createElementNS(premis_ns, "objectIdentifier")
    object_element.appendChild(object_identifier_element)

    object_identifier_type_element = doc.createElementNS(premis_ns, "objectIdentifierType")
    object_identifier_type_element.appendChild(doc.createTextNode('URI'))
    object_identifier_element.appendChild(object_identifier_type_element)

    object_identifier_value_element = doc.createElementNS(premis_ns, "objectIdentifierValue")
    object_identifier_value_element.appendChild(doc.createTextNode(file[0]))
    object_identifier_element.appendChild(object_identifier_value_element)

    object_characteristics_element = doc.createElementNS(premis_ns, "objectCharacteristics")
    object_element.appendChild(object_characteristics_element)

    fixity_element = doc.createElementNS(premis_ns, "fixity")
    object_characteristics_element.appendChild(fixity_element)

    message_digest_algorithm_element = doc.createElementNS(premis_ns, "messageDigestAlgorithm")
    message_digest_algorithm_element.appendChild(doc.createTextNode('MD5'))
    fixity_element.appendChild(message_digest_algorithm_element)

    md5 = hashlib.md5(file[0]).hexdigest()
    message_digest_element = doc.createElementNS(premis_ns, "messageDigest")
    message_digest_element.appendChild(doc.createTextNode(md5))
    fixity_element.appendChild(message_digest_element)

# We want to create an <event> element for each commit. We also populate
# a dictionay containing Agent information taken from the commit authors'
# name and email address.
agents = {}
for file in files:
    for k, l in repo_history[file[0]].iteritems():

        if l[1] not in agents:
            agents[l[1]] = l[0]

        event_element = doc.createElementNS(premis_ns, "event")
        premis_element.appendChild(event_element)

        event_identifier_element = doc.createElementNS(premis_ns, "eventIdentifier")
        event_element.appendChild(event_identifier_element)

        event_identifier_type_element = doc.createElementNS(premis_ns, "eventIdentifierType")
        event_identifier_type_element.appendChild(doc.createTextNode('SHA-1'))
        event_identifier_element.appendChild(event_identifier_type_element)

        event_identifier_value_element = doc.createElementNS(premis_ns, "eventIdentifierValue")
        event_identifier_value_element.appendChild(doc.createTextNode(k))
        event_identifier_element.appendChild(event_identifier_value_element)

        event_type_element = doc.createElementNS(premis_ns, "eventType")
        event_type_element.appendChild(doc.createTextNode('Git commit'))
        event_element.appendChild(event_type_element)

        event_detail_element = doc.createElementNS(premis_ns, "eventDetail")
        event_detail_element.appendChild(doc.createTextNode(l[3]))
        event_element.appendChild(event_detail_element)

        event_datetime_element = doc.createElementNS(premis_ns, "eventDateTime")
        event_datetime_element.appendChild(doc.createTextNode(l[2]))
        event_element.appendChild(event_datetime_element)

        linking_object_identifier_element = doc.createElementNS(premis_ns, "linkingObjectIdentifier")
        event_element.appendChild(linking_object_identifier_element)

        linking_object_identifier_type_element = doc.createElementNS(premis_ns, "linkingObjectIdentifierType")
        linking_object_identifier_type_element.appendChild(doc.createTextNode('URI'))
        event_element.appendChild(linking_object_identifier_type_element)
        linking_object_identifier_element.appendChild(linking_object_identifier_type_element)

        linking_object_identifier_value_element = doc.createElementNS(premis_ns, "linkingObjectIdentifierValue")
        linking_object_identifier_value_element.appendChild(doc.createTextNode(file[0]))
        linking_object_identifier_element.appendChild(linking_object_identifier_value_element)

        linking_agent_identifier_element = doc.createElementNS(premis_ns, "linkingAgentdentifier")
        event_element.appendChild(linking_agent_identifier_element)

        linking_agent_identifier_type_element = doc.createElementNS(premis_ns, "linkingAgentIdentifierType")
        linking_agent_identifier_type_element.appendChild(doc.createTextNode('Email address'))
        linking_agent_identifier_element.appendChild(linking_agent_identifier_type_element)

        linking_agent_identifier_value_element = doc.createElementNS(premis_ns, "linkingAgentIdentifierValue")
        linking_agent_identifier_value_element.appendChild(doc.createTextNode(l[1]))
        linking_agent_identifier_element.appendChild(linking_agent_identifier_value_element)

# We create an agent element for each memeber of the agents dictionary populated above.
for email, name in agents.iteritems():
        agent_element = doc.createElementNS(premis_ns, "agent")
        premis_element.appendChild(agent_element)

        agent_identifier_element = doc.createElementNS(premis_ns, "agentIdentifer")
        agent_element.appendChild(agent_identifier_element)

        agent_identifier_type_element = doc.createElementNS(premis_ns, "agentIdentifierType")
        agent_identifier_type_element.appendChild(doc.createTextNode('Email address'))
        agent_identifier_element.appendChild(agent_identifier_type_element)

        agent_identifier_value_element = doc.createElementNS(premis_ns, "agentIdentifierValue")
        agent_identifier_value_element.appendChild(doc.createTextNode(email))
        agent_identifier_element.appendChild(agent_identifier_value_element)

        agent_name_element = doc.createElementNS(premis_ns, "agentName")
        agent_name_element.appendChild(doc.createTextNode(name))
        agent_element.appendChild(agent_name_element)

print doc.toprettyxml(indent='  ')

