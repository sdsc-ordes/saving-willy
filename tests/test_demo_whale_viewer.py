from streamlit.testing.v1 import AppTest
import pytest # for the exception testing

import whale_viewer # for data


def test_selectbox_ok():
    '''
    test the snippet demoing whale viewer - relating to AppTest'able elements
    
    we validate that
    - there is one selectbox present, with initial value "beluga" and index 0
    - the two markdown elems generated dynamically by the selection corresponds
    
    - then changing the selection, we do the same checks again

    - finally, we check there are the right number of options (26)
    
    '''
    at = AppTest.from_file("src/apptest/demo_whale_viewer.py").run()
    assert len(at.selectbox) == 1
    assert at.selectbox[0].value == "beluga"
    assert at.selectbox[0].index == 0
    
    # let's check that the markdown is right
    # the first markdown should be "Selected species: beluga"
    assert at.markdown[0].value == "Selected species: beluga"
    # the second markdown should be "### :whale:  #1: Beluga"
    print("markdown 1: ", at.markdown[1].value)
    assert at.markdown[1].value == ":whale:  #1: Beluga"

    # now let's select a different element. index 4 is commersons_dolphin
    v4 = "commersons_dolphin"
    v4_str = v4.replace("_", " ").title()
    
    at.selectbox[0].set_value(v4).run()
    assert at.selectbox[0].value == v4
    assert at.selectbox[0].index == 4
    # the first markdown should be "Selected species: commersons_dolphin"
    assert at.markdown[0].value == f"Selected species: {v4}"
    # the second markdown should be "### :whale:  #1: Commersons Dolphin"
    assert at.markdown[1].value == f":whale:  #1: {v4_str}"
    
    # test there are the right number of options
    print("PROPS=> ", dir(at.selectbox[0])) # no length unfortunately,
    # test it dynamically intead.
    # should be fine
    at.selectbox[0].select_index(len(whale_viewer.WHALE_CLASSES)-1).run()
    # should fail
    with pytest.raises(Exception):
        at.selectbox[0].select_index(len(whale_viewer.WHALE_CLASSES)).run()
    
def test_img_props():
    '''
    test the snippet demoing whale viewer - relating to the image 
    
    we validate that
    - one image is displayed
    - the caption corresponds to the data in WHALE_REFERENCES
    - the url is a mock url
    
    - then changing the image, we do the same checks again
    
    '''
    at = AppTest.from_file("src/apptest/demo_whale_viewer.py").run()
    ix = 0 # we didn't interact with the dropdown, so it should be the first one
    # could fetch the property - maybe better in case code example changes
    ix = at.selectbox[0].index 
    
    elem = at.get("imgs") # hmm, apparently the naming is not consistent with the other AppTest f/w. 
    # type(elem[0]) -> "streamlit.testing.v1.element_tree.UnknownElement" haha
    assert len(elem) == 1 
    img0 = elem[0]

    # we can't check the image, but maybe the alt text?
    #assert at.image[0].alt == "beluga" # no, doesn't have that property.

    # for v1.39, the proto comes back something like this:
    exp_proto = '''
        imgs {
        caption: "https://www.fisheries.noaa.gov/species/beluga-whale"
        url: "/mock/media/6a21db178fcd99b82817906fc716a5c35117f4daa1d1c1d3c16ae1c8.png"
        }
        width: -3
    '''
    # from the proto string we can look for <itemtype>: "<value>" pairs and make a dictionary
    import re

    def parse_proto(proto_str):
        pattern = r'(\w+):\s*"([^"]+)"'
        matches = re.findall(pattern, proto_str)
        return {key: value for key, value in matches}

    parsed_proto = parse_proto(str(img0.proto))
    # we're expecting the caption to be WHALE_REFERENCES[ix]
    print(parsed_proto)
    assert "caption" in parsed_proto
    assert parsed_proto["caption"] == whale_viewer.WHALE_REFERENCES[ix]
    assert "url" in parsed_proto
    assert parsed_proto["url"].startswith("/mock/media")
    
    print(whale_viewer.WHALE_REFERENCES[ix])

    # now let's switch to another index
    ix = 15
    v15 = whale_viewer.WHALE_CLASSES[ix]
    v15_str = v15.replace("_", " ").title()
    at.selectbox[0].set_value(v15).run()
    
    elem = at.get("imgs") 
    img0 = elem[0]
    print("[INFO] image 0 after adjusting dropdown:")
    print(img0.type, type(img0.proto))#, "\t", i0.value) # it doesn't have a value
    print(img0.proto)
    
    
    parsed_proto = parse_proto(str(img0.proto))
    # we're expecting the caption to be WHALE_REFERENCES[ix]
    print(parsed_proto)
    assert "caption" in parsed_proto
    assert parsed_proto["caption"] == whale_viewer.WHALE_REFERENCES[ix]
    assert "url" in parsed_proto
    assert parsed_proto["url"].startswith("/mock/media")
    


    


