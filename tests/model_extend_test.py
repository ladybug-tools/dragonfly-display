"""Test the Model to_vis_set method."""
from ladybug_display.geometry3d import DisplayMesh3D, DisplayLineSegment3D, \
    DisplayText3D
from ladybug_display.visualization import VisualizationSet, \
    ContextGeometry, AnalysisGeometry, VisualizationData
from dragonfly.model import Model
from honeybee_display.attr import RoomAttribute, FaceAttribute


def test_default_to_vis_set():
    """Test the default output of Model.to_vis_set()."""
    model_json = './tests/json/model_with_doors_skylights.dfjson'
    parsed_model = Model.from_dfjson(model_json)
    vis_set = parsed_model.to_vis_set()

    assert isinstance(vis_set, VisualizationSet)
    assert len(vis_set) == 10
    for geo_obj in vis_set[:-1]:
        assert isinstance(geo_obj, ContextGeometry)
        assert isinstance(geo_obj[0], DisplayMesh3D)
    assert isinstance(vis_set[-1], ContextGeometry)
    assert vis_set[-1].display_name == 'Wireframe'
    assert isinstance(vis_set[-1][0], DisplayLineSegment3D)

    vis_set = parsed_model.to_vis_set(include_wireframe=False)
    assert len(vis_set) == 9
    for geo_obj in vis_set:
        assert isinstance(geo_obj, ContextGeometry)
        assert isinstance(geo_obj[0], DisplayMesh3D)

    vis_set = parsed_model.to_vis_set(color_by='none')
    assert len(vis_set) == 1
    for geo_obj in vis_set:
        assert isinstance(geo_obj, ContextGeometry)
        assert isinstance(geo_obj[0], DisplayLineSegment3D)

    vis_set = parsed_model.to_vis_set(
        color_by='boundary_condition', include_wireframe=False)
    assert len(vis_set) == 5
    for geo_obj in vis_set:
        assert isinstance(geo_obj, ContextGeometry)
        assert isinstance(geo_obj[0], DisplayMesh3D)


def test_room_attr_to_vis_set():
    """Test the room attribute argument of Model.to_vis_set()."""
    model_json = './tests/json/model_with_doors_skylights.dfjson'
    parsed_model = Model.from_dfjson(model_json)
    attr_color = RoomAttribute(
        name='Floor Area', attrs=['floor_area'], text=False, color=True)
    vis_set = parsed_model.to_vis_set(color_by='none', room_attrs=[attr_color])

    assert isinstance(vis_set[0], AnalysisGeometry)
    assert isinstance(vis_set[0][0], VisualizationData)
    assert len(vis_set[0][0].values) == 15
    attr_txt = RoomAttribute(
        name='Floor Area', attrs=['floor_area'], text=True, color=False)
    vis_set = parsed_model.to_vis_set(color_by='none', room_attrs=[attr_txt])
    assert isinstance(vis_set[0], ContextGeometry)
    assert len(vis_set[0]) == 15
    for item in vis_set[0]:
        assert isinstance(item, DisplayText3D)


def test_face_attr_to_vis_set():
    """Test the face attribute argument of Model.to_vis_set()."""
    model_json = './tests/json/model_with_doors_skylights.dfjson'
    parsed_model = Model.from_dfjson(model_json)
    attr_color = FaceAttribute(name='Area', attrs=['area'], color=True, text=False)
    vis_set = parsed_model.to_vis_set(color_by='None', face_attrs=[attr_color])
    assert isinstance(vis_set[0], AnalysisGeometry)
    assert isinstance(vis_set[0][0], VisualizationData)
    assert len(vis_set[0][0].values) == 324

    attr_txt = FaceAttribute(name='Area', attrs=['area'], color=False, text=True)
    vis_set = parsed_model.to_vis_set(color_by='None', face_attrs=[attr_txt])
    assert isinstance(vis_set[0], ContextGeometry)
    assert len(vis_set[0]) == 324
    for item in vis_set[0]:
        assert isinstance(item, DisplayText3D)
