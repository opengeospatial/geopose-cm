Here are instructions to co-pilot for refactoring the content of this repository. 

The current content of the present repository is mostly the same as the GeoPose 1.0 original standard published here https://docs.ogc.org/is/21-056r11/21-056r11.html. The document is generated based on this repository https://github.com/opengeospatial/GeoPose 

Most content pertaining to JSON Encoding and conformance testing has been removed from this repository. 

In order to make OGC standards more easily used, a goal for future standards is to reduce complexity for implementors by opening the complete conceptual model into the smallest meaningful and resuable units. Once atomic components are defined in a standard, they may be referenced elsewhere in other standards, or in implementations. The standard defines how components are tested for conformance.

The purpose of this project is to build a new specification in this repository focusing on the GeoPose Conceptual and Logical Model that is already set up with Metanorma for publishing as an official OGC document. In addition, as part of the input to the new specification, this project provides images and text about the GeoPose Components in the refactoring-resources folder. /workspaces/geopose-cm/refactoring-resources

The GeoPose Conceptual and Logical Model that this new specification will describe will always be backward compatible with the GeoPose Standard 1.0. The new specification will retain many parts of the original GeoPose 1.0 Data Exchange Standard. Specifically, new specification will have the same as GeoPose 1.0:
- License Agreement 
- Keywords (maybe add some?)
- Preface
- Security Considerations
- Conventions (Clause 5) 
- Use cases (Clause 6.4)
- Logical Model (Clause 7) except where mentioned below.
- Annex D will remain a glossary.
