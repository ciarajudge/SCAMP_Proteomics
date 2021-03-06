#!/usr/bin/env python
"""
WordAPI.py
Copyright 2014 Wordnik, Inc.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

NOTE: This class is auto generated by the swagger code generator program. Do not edit the class manually.
"""
import sys
import os

from models import *


class ProjectApi(object):

    def __init__(self, apiClient):
      self.apiClient = apiClient

    

    def getProjectSummary(self, projectAccession, **kwargs):
        """retrieve project information by accession

        Args:
            projectAccession, str: a project accession number (example: PXD000001) (required)

            

        Returns: ProjectDetail
        """

        allParams = ['projectAccession']

        params = locals()
        for (key, val) in params['kwargs'].iteritems():
            if key not in allParams:
                raise TypeError("Got an unexpected keyword argument '%s' to method getProjectSummary" % key)
            params[key] = val
        del params['kwargs']

        resourcePath = '/project/{projectAccession}'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'

        queryParams = {}
        headerParams = {}
        formParams = {}
        bodyParam = None

        if ('projectAccession' in params):
            replacement = str(self.apiClient.toPathValue(params['projectAccession']))
            resourcePath = resourcePath.replace('{' + 'projectAccession' + '}',
                                                replacement)
        if formParams:
            headerParams['Content-type'] = 'application/x-www-form-urlencoded'

        postData = (formParams if formParams else bodyParam)

        response = self.apiClient.callAPI(resourcePath, method, queryParams,
                                          postData, headerParams)

        if not response:
            return None
	return response
        responseObject = self.apiClient.deserialize(response, 'ProjectDetail')
        return responseObject
        

        

    def simpleSearchProjects(self, show= None, page= None, order= None, **kwargs):
        """list projects for given criteria

        Args:
            query, str: search term to query for (example: stress) (optional)

            sort, str: the field to sort on (e.g. score, publication_date, id or project_title) (optional)

            speciesFilter, list[str]: filter by species (NCBI taxon ID, example: 9606 for human) (optional)

            ptmsFilter, list[str]: filter by PTM annotation (example: phosphorylation) (optional)

            tissueFilter, list[str]: filter by tissue annotation (example: brain) (optional)

            diseaseFilter, list[str]: filter by disease annotation (example: cancer) (optional)

            titleFilter, list[str]: filter the title for keywords (example: stress) (optional)

            instrumentFilter, list[str]: filter for instrument names or keywords (example: ltq) (optional)

            experimentTypeFilter, list[str]: filter by experiment type (example: shotgun) (optional)

            quantificationFilter, list[str]: filter by quantification annotation (example: label-free) (optional)

            projectTagFilter, list[str]: filter by project tags (example: Biomedical) (optional)

            show, int: how many results to return per page (required)

            page, int: which page (starting from 0) of the result to return (required)

            order, str: the sorting order (asc or desc) (required)

            

        Returns: ProjectSummaryList
        """

        allParams = ['query', 'sort', 'speciesFilter', 'ptmsFilter', 'tissueFilter', 'diseaseFilter', 'titleFilter', 'instrumentFilter', 'experimentTypeFilter', 'quantificationFilter', 'projectTagFilter', 'show', 'page', 'order']

        params = locals()
        for (key, val) in params['kwargs'].iteritems():
            if key not in allParams:
                raise TypeError("Got an unexpected keyword argument '%s' to method simpleSearchProjects" % key)
            params[key] = val
        del params['kwargs']

        resourcePath = '/project/list'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'

        queryParams = {}
        headerParams = {}
        formParams = {}
        bodyParam = None

        if ('query' in params):
            queryParams['query'] = self.apiClient.toPathValue(params['query'])
        if ('show' in params):
            queryParams['show'] = self.apiClient.toPathValue(params['show'])
        if ('page' in params):
            queryParams['page'] = self.apiClient.toPathValue(params['page'])
        if ('sort' in params):
            queryParams['sort'] = self.apiClient.toPathValue(params['sort'])
        if ('order' in params):
            queryParams['order'] = self.apiClient.toPathValue(params['order'])
        if ('speciesFilter' in params):
            queryParams['speciesFilter'] = self.apiClient.toPathValue(params['speciesFilter'])
        if ('ptmsFilter' in params):
            queryParams['ptmsFilter'] = self.apiClient.toPathValue(params['ptmsFilter'])
        if ('tissueFilter' in params):
            queryParams['tissueFilter'] = self.apiClient.toPathValue(params['tissueFilter'])
        if ('diseaseFilter' in params):
            queryParams['diseaseFilter'] = self.apiClient.toPathValue(params['diseaseFilter'])
        if ('titleFilter' in params):
            queryParams['titleFilter'] = self.apiClient.toPathValue(params['titleFilter'])
        if ('instrumentFilter' in params):
            queryParams['instrumentFilter'] = self.apiClient.toPathValue(params['instrumentFilter'])
        if ('experimentTypeFilter' in params):
            queryParams['experimentTypeFilter'] = self.apiClient.toPathValue(params['experimentTypeFilter'])
        if ('quantificationFilter' in params):
            queryParams['quantificationFilter'] = self.apiClient.toPathValue(params['quantificationFilter'])
        if ('projectTagFilter' in params):
            queryParams['projectTagFilter'] = self.apiClient.toPathValue(params['projectTagFilter'])
        if formParams:
            headerParams['Content-type'] = 'application/x-www-form-urlencoded'

        postData = (formParams if formParams else bodyParam)

        response = self.apiClient.callAPI(resourcePath, method, queryParams,
                                          postData, headerParams)

        if not response:
            return None

        responseObject = self.apiClient.deserialize(response, 'ProjectSummaryList')
        return responseObject
        

        

    def countSearchProjects(self, **kwargs):
        """count projects for given criteria

        Args:
            query, str: search term to query for (example: stress) (optional)

            speciesFilter, list[str]: filter by species (NCBI taxon ID, example: 9606 for human) (optional)

            ptmsFilter, list[str]: filter by PTM annotation (example: phosphorylation) (optional)

            tissueFilter, list[str]: filter by tissue annotation (example: brain) (optional)

            diseaseFilter, list[str]: filter by disease annotation (example: cancer) (optional)

            titleFilter, list[str]: filter the title for keywords (example: stress) (optional)

            instrumentFilter, list[str]: filter for instrument names or keywords (example: ltq) (optional)

            experimentTypeFilter, list[str]: filter by experiment type (example: shotgun) (optional)

            quantificationFilter, list[str]: filter by quantification annotation (example: label-free) (optional)

            projectTagFilter, list[str]: filter by project tags (example: Biomedical) (optional)

            

        Returns: long
        """

        allParams = ['query', 'speciesFilter', 'ptmsFilter', 'tissueFilter', 'diseaseFilter', 'titleFilter', 'instrumentFilter', 'experimentTypeFilter', 'quantificationFilter', 'projectTagFilter']

        params = locals()
        for (key, val) in params['kwargs'].iteritems():
            if key not in allParams:
                raise TypeError("Got an unexpected keyword argument '%s' to method countSearchProjects" % key)
            params[key] = val
        del params['kwargs']

        resourcePath = '/project/count'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'

        queryParams = {}
        headerParams = {}
        formParams = {}
        bodyParam = None

        if ('query' in params):
            queryParams['query'] = self.apiClient.toPathValue(params['query'])
        if ('speciesFilter' in params):
            queryParams['speciesFilter'] = self.apiClient.toPathValue(params['speciesFilter'])
        if ('ptmsFilter' in params):
            queryParams['ptmsFilter'] = self.apiClient.toPathValue(params['ptmsFilter'])
        if ('tissueFilter' in params):
            queryParams['tissueFilter'] = self.apiClient.toPathValue(params['tissueFilter'])
        if ('diseaseFilter' in params):
            queryParams['diseaseFilter'] = self.apiClient.toPathValue(params['diseaseFilter'])
        if ('titleFilter' in params):
            queryParams['titleFilter'] = self.apiClient.toPathValue(params['titleFilter'])
        if ('instrumentFilter' in params):
            queryParams['instrumentFilter'] = self.apiClient.toPathValue(params['instrumentFilter'])
        if ('experimentTypeFilter' in params):
            queryParams['experimentTypeFilter'] = self.apiClient.toPathValue(params['experimentTypeFilter'])
        if ('quantificationFilter' in params):
            queryParams['quantificationFilter'] = self.apiClient.toPathValue(params['quantificationFilter'])
        if ('projectTagFilter' in params):
            queryParams['projectTagFilter'] = self.apiClient.toPathValue(params['projectTagFilter'])
        if formParams:
            headerParams['Content-type'] = 'application/x-www-form-urlencoded'

        postData = (formParams if formParams else bodyParam)

        response = self.apiClient.callAPI(resourcePath, method, queryParams,
                                          postData, headerParams)

        if not response:
            return None

        responseObject = self.apiClient.deserialize(response, 'long')
        return responseObject
        

        

    




