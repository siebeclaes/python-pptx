# encoding: utf-8

"""
lxml custom element classes for slide-related XML elements, including all
masters.
"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

from . import parse_from_template, parse_xml
from .ns import nsdecls
from .simpletypes import XsdString
from .xmlchemy import (
    BaseOxmlElement, OneAndOnlyOne, OptionalAttribute, RequiredAttribute,
    ZeroOrMore, ZeroOrOne
)


class _BaseSlideElement(BaseOxmlElement):
    """
    Base class for the six slide types, providing common methods.
    """
    @property
    def spTree(self):
        """
        Return required `p:cSld/p:spTree` grandchild.
        """
        return self.cSld.spTree


class CT_CommonSlideData(BaseOxmlElement):
    """
    ``<p:cSld>`` element.
    """
    _tag_seq = (
        'p:bg', 'p:spTree', 'p:custDataLst', 'p:controls', 'p:extLst'
    )
    spTree = OneAndOnlyOne('p:spTree')
    del _tag_seq

    name = OptionalAttribute('name', XsdString, default='')


class CT_NotesMaster(_BaseSlideElement):
    """
    ``<p:notesMaster>`` element, root of a notes master part
    """
    _tag_seq = ('p:cSld', 'p:clrMap', 'p:hf', 'p:notesStyle', 'p:extLst')
    cSld = OneAndOnlyOne('p:cSld')
    del _tag_seq

    @classmethod
    def new_default(cls):
        """
        Return a new ``<p:notesMaster>`` element based on the built-in
        default template.
        """
        return parse_from_template('notesMaster')


class CT_NotesSlide(_BaseSlideElement):
    """
    ``<p:notes>`` element, root of a notes slide part
    """
    _tag_seq = ('p:cSld', 'p:clrMapOvr', 'p:extLst')
    cSld = OneAndOnlyOne('p:cSld')
    del _tag_seq

    @classmethod
    def new(cls):
        """
        Return a new ``<p:notes>`` element based on the default template.
        Note that the template does not include placeholders, which must be
        subsequently cloned from the notes master.
        """
        return parse_from_template('notes')


class CT_Slide(_BaseSlideElement):
    """`p:sld` element, root element of a slide part (XML document)."""

    _tag_seq = (
        'p:cSld', 'p:clrMapOvr', 'p:transition', 'p:timing', 'p:extLst'
    )
    cSld = OneAndOnlyOne('p:cSld')
    clrMapOvr = ZeroOrOne('p:clrMapOvr', successors=_tag_seq[2:])
    timing = ZeroOrOne('p:timing', successors=_tag_seq[4:])
    del _tag_seq

    @classmethod
    def new(cls):
        """
        Return a new ``<p:sld>`` element configured as a base slide shape.
        """
        return parse_xml(cls._sld_xml())

    def get_or_add_childTnLst(self):
        """Return parent element for a new `p:video` child element.

        The `p:video` element causes play controls to appear under a video
        shape (pic shape containing video). There can be more than one video
        shape on a slide, which causes the precondition to vary. It needs to
        handle the case when there is no `p:sld/p:timing` element and when
        that element already exists. If the case isn't simple, it just nukes
        what's there and adds a fresh one. This could theoretically remove
        desired existing timing information, but there isn't any evidence
        available to me one way or the other, so I've taken the simple
        approach.
        """
        childTnLst = self._childTnLst
        if childTnLst is None:
            childTnLst = self._add_childTnLst()
        return childTnLst

    def _add_childTnLst(self):
        """Add `./p:timing/p:tnLst/p:par/p:cTn/p:childTnLst` descendant.

        Any existing `p:timing` child element is ruthlessly removed and
        replaced.
        """
        self.remove(self.get_or_add_timing())
        timing = parse_xml(self._childTnLst_timing_xml())
        self._insert_timing(timing)
        return timing.xpath('./p:tnLst/p:par/p:cTn/p:childTnLst')[0]

    @property
    def _childTnLst(self):
        """Return `./p:timing/p:tnLst/p:par/p:cTn/p:childTnLst` descendant.

        Return None if that element is not present.
        """
        childTnLsts = self.xpath(
            './p:timing/p:tnLst/p:par/p:cTn/p:childTnLst'
        )
        if not childTnLsts:
            return None
        return childTnLsts[0]

    @staticmethod
    def _childTnLst_timing_xml():
        return (
            '<p:timing %s>\n'
            '  <p:tnLst>\n'
            '    <p:par>\n'
            '      <p:cTn id="1" dur="indefinite" restart="never" nodeType="'
            'tmRoot">\n'
            '        <p:childTnLst/>\n'
            '      </p:cTn>\n'
            '    </p:par>\n'
            '  </p:tnLst>\n'
            '</p:timing>' % nsdecls('p')
        )

    @staticmethod
    def _sld_xml():
        return (
            '<p:sld %s>\n'
            '  <p:cSld>\n'
            '    <p:spTree>\n'
            '      <p:nvGrpSpPr>\n'
            '        <p:cNvPr id="1" name=""/>\n'
            '        <p:cNvGrpSpPr/>\n'
            '        <p:nvPr/>\n'
            '      </p:nvGrpSpPr>\n'
            '      <p:grpSpPr/>\n'
            '    </p:spTree>\n'
            '  </p:cSld>\n'
            '  <p:clrMapOvr>\n'
            '    <a:masterClrMapping/>\n'
            '  </p:clrMapOvr>\n'
            '</p:sld>' % nsdecls('a', 'p', 'r')
        )


class CT_SlideLayout(_BaseSlideElement):
    """
    ``<p:sldLayout>`` element, root of a slide layout part
    """
    _tag_seq = (
        'p:cSld', 'p:clrMapOvr', 'p:transition', 'p:timing', 'p:hf',
        'p:extLst'
    )
    cSld = OneAndOnlyOne('p:cSld')
    del _tag_seq


class CT_SlideLayoutIdList(BaseOxmlElement):
    """
    ``<p:sldLayoutIdLst>`` element, child of ``<p:sldMaster>`` containing
    references to the slide layouts that inherit from the slide master.
    """
    sldLayoutId = ZeroOrMore('p:sldLayoutId')


class CT_SlideLayoutIdListEntry(BaseOxmlElement):
    """
    ``<p:sldLayoutId>`` element, child of ``<p:sldLayoutIdLst>`` containing
    a reference to a slide layout.
    """
    rId = RequiredAttribute('r:id', XsdString)


class CT_SlideMaster(_BaseSlideElement):
    """
    ``<p:sldMaster>`` element, root of a slide master part
    """
    _tag_seq = (
        'p:cSld', 'p:clrMap', 'p:sldLayoutIdLst', 'p:transition', 'p:timing',
        'p:hf', 'p:txStyles', 'p:extLst'
    )
    cSld = OneAndOnlyOne('p:cSld')
    sldLayoutIdLst = ZeroOrOne('p:sldLayoutIdLst', successors=_tag_seq[3:])
    del _tag_seq


class CT_SlideTiming(BaseOxmlElement):
    """`p:timing` element, specifying animations and timed behaviors."""

    _tag_seq = ('p:tnLst', 'p:bldLst', 'p:extLst')
    tnLst = ZeroOrOne('p:tnLst', successors=_tag_seq[1:])
    del _tag_seq


class CT_TimeNodeList(BaseOxmlElement):
    """`p:tnLst` or `p:childTnList` element."""
    
    def add_audio(self, shape_id, duration):
        """Add a new `p:audio` child element for audio pic having *shape_id*."""
        ctnId = self._next_cTn_id
        seq_xml = (
            '<p:seq concurrent="1" nextAc="seek" %s>\n'
            '    <p:cTn id="%d" dur="indefinite" nodeType="mainSeq">\n'
            '      <p:childTnLst>\n'
            '        <p:par>\n'
            '          <p:cTn id="%d" fill="hold">\n'
            '            <p:stCondLst>\n'
            '              <p:cond delay="indefinite"/>\n'
            '            </p:stCondLst>\n'
            '            <p:childTnLst>\n'
            '              <p:par>\n'
            '                <p:cTn id="%d" fill="hold">\n' '                  <p:stCondLst>\n'
            '                    <p:cond delay="0"/>\n'
            '                  </p:stCondLst>\n'
            '                  <p:childTnLst>\n'
            '                    <p:par>\n'
            '                      <p:cTn id="%d" presetID="1" presetClass="mediacall" presetSubtype="0" fill="hold" nodeType="clickEffect">\n'
            '                        <p:stCondLst>\n'
            '                          <p:cond delay="0"/>\n'
            '                        </p:stCondLst>\n'
            '                        <p:childTnLst>\n'
            '                          <p:cmd type="call" cmd="playFrom(0.0)">\n'
            '                            <p:cBhvr>\n'
            '                              <p:cTn id="%d" dur="%d" fill="hold"/>\n'
            '                              <p:tgtEl>\n'
            '                                <p:spTgt spid="%d"/>\n'
            '                              </p:tgtEl>\n'
            '                            </p:cBhvr>\n'
            '                          </p:cmd>\n'
            '                        </p:childTnLst>\n'
            '                      </p:cTn>\n'
            '                    </p:par>\n'
            '                  </p:childTnLst>\n'
            '                </p:cTn>\n'
            '              </p:par>\n'
            '            </p:childTnLst>\n'
            '          </p:cTn>\n'
            '        </p:par>\n'
            '      </p:childTnLst>\n'
            '    </p:cTn>\n'
            '    <p:prevCondLst>\n'
            '      <p:cond evt="onPrev" delay="0">\n'
            '      <p:tgtEl>\n'
            '        <p:sldTgt/>\n'
            '      </p:tgtEl>\n'
            '     </p:cond>\n'
            '    </p:prevCondLst>\n'
            '    <p:nextCondLst>\n'
            '      <p:cond evt="onNext" delay="0">\n'
            '        <p:tgtEl>\n'
            '          <p:sldTgt/>\n'
            '        </p:tgtEl>\n'
            '      </p:cond>\n'
            '    </p:nextCondLst>\n'
            '    </p:seq>\n' % (nsdecls('p'), ctnId, ctnId+1, ctnId+2, ctnId+3, ctnId+4, duration, shape_id)
        )
        audio_xml = (
            '<p:audio %s>\n'
            '    <p:cMediaNode vol="80000" showWhenStopped="0">\n'
            '      <p:cTn id="%d" display="0">\n'
            '        <p:stCondLst>\n'
            '          <p:cond delay="indefinite"/>\n'
            '        </p:stCondLst>\n'
            '        <p:endCondLst>\n'
            '          <p:cond evt="onStopAudio" delay="0">\n'
            '            <p:tgtEl>\n'
            '              <p:sldTgt/>\n'
            '            </p:tgtEl>\n'
            '          </p:cond>\n'
            '        </p:endCondLst>\n'
            '      </p:cTn>\n'
            '      <p:tgtEl>\n'
            '        <p:spTgt spid="%d"/>\n'
            '      </p:tgtEl>\n'
            '    </p:cMediaNode>\n'
            '</p:audio>\n' % (nsdecls('p'), ctnId+5, shape_id)
        )
        seq = parse_xml(seq_xml)
        audio = parse_xml(audio_xml)

        self.append(seq)
        self.append(audio)

    def add_video(self, shape_id):
        """Add a new `p:video` child element for movie having *shape_id*."""
        video_xml = (
            '<p:video %s>\n'
            '  <p:cMediaNode vol="80000">\n'
            '    <p:cTn id="%d" fill="hold" display="0">\n'
            '      <p:stCondLst>\n'
            '        <p:cond delay="indefinite"/>\n'
            '      </p:stCondLst>\n'
            '    </p:cTn>\n'
            '    <p:tgtEl>\n'
            '      <p:spTgt spid="%d"/>\n'
            '    </p:tgtEl>\n'
            '  </p:cMediaNode>\n'
            '</p:video>\n' % (nsdecls('p'), self._next_cTn_id, shape_id)
        )
        video = parse_xml(video_xml)
        self.append(video)

    def add_video_play_onclick(self, shape_id, video_length):
        """Add a new `p:seq` child element for movie havind *shape_id* and length *video_length* in ms."""
        seq_xml = (
            '<p:seq concurrent="1" nextAc="seek" %s>\n'
            '  <p:cTn id="%d" dur="indefinite" nodeType="mainSeq">\n'
            '	<p:childTnLst>\n'
            '	  <p:par>\n'
            '		<p:cTn id="%d" fill="hold">\n'
            '		  <p:stCondLst>\n'
            '			<p:cond delay="indefinite"/>\n'
            '		  </p:stCondLst>\n'
            '		  <p:childTnLst>\n'
            '			<p:par>\n'
            '			  <p:cTn id="%d" fill="hold">\n'
            '				<p:stCondLst>\n'
            '				  <p:cond delay="0"/>\n'
            '				</p:stCondLst>\n'
            '				<p:childTnLst>\n'
            '				  <p:par>\n'
            '					<p:cTn id="%d" presetID="1" presetClass="mediacall" presetSubtype="0" fill="hold" nodeType="clickEffect">\n'
            '					  <p:stCondLst>\n'
            '						<p:cond delay="0"/>\n'
            '					  </p:stCondLst>\n'
            '					  <p:childTnLst>\n'
            '						<p:cmd type="call" cmd="playFrom(0.0)">\n'
            '						  <p:cBhvr>\n'
            '							<p:cTn id="%d" dur="%d" fill="hold"/>\n'
            '							<p:tgtEl>\n'
            '							  <p:spTgt spid="%d"/>\n'
            '							</p:tgtEl>\n'
            '						  </p:cBhvr>\n'
            '						</p:cmd>\n'
            '					  </p:childTnLst>\n'
            '					</p:cTn>\n'
            '				  </p:par>\n'
            '				</p:childTnLst>\n'
            '			  </p:cTn>\n'
            '			</p:par>\n'
            '		  </p:childTnLst>\n'
            '		</p:cTn>\n'
            '	  </p:par>\n'
            '	</p:childTnLst>\n'
            '  </p:cTn>\n'
            '  <p:prevCondLst>\n'
            '	<p:cond evt="onPrev" delay="0">\n'
            '	  <p:tgtEl>\n'
            '		<p:sldTgt/>\n'
            '	  </p:tgtEl>\n'
            '	</p:cond>\n'
            '  </p:prevCondLst>\n'
            '  <p:nextCondLst>\n'
            '	<p:cond evt="onNext" delay="0">\n'
            '	  <p:tgtEl>\n'
            '		<p:sldTgt/>\n'
            '	  </p:tgtEl>\n'
            '	</p:cond>\n'
            '  </p:nextCondLst>\n'
            '</p:seq>\n' % (nsdecls('p'), self._next_cTn_id, self._next_cTn_id, self._next_cTn_id, self._next_cTn_id, self._next_cTn_id, video_length, shape_id)
        )
        seq = parse_xml(seq_xml)
        self.append(seq)

    @property
    def _childTnLst(self):
        """Return `./p:seq/p:cTn/p:childTnLst` descendant.

        Return None if that element is not present.
        """
        childTnLsts = self.xpath(
            './p:seq/p:cTn/p:childTnLst'
        )
        if not childTnLsts:
            return None
        return childTnLsts[0]

    def add_textbox_appear(self, shape_id):
        """Add a new `p:seq` child element for shape havind *shape_id* so that it appears after *delay* ms"""
        ctnId = self._next_cTn_id
        first_seq_childTnLst = self._childTnLst
        anim_xml = ('<p:par %s>\n'
                    '	<p:cTn id="%d" fill="hold">\n'
                    '		<p:stCondLst>\n'
                    '			<p:cond delay="indefinite"/>\n'
                    '		</p:stCondLst>\n'
                    '		<p:childTnLst>\n'
                    '			<p:par>\n'
                    '				<p:cTn id="%d" fill="hold">\n'
                    '				<p:stCondLst>\n'
                    '					<p:cond delay="0"/>\n'
                    '				</p:stCondLst>\n'
                    '				<p:childTnLst>\n'
                    '					<p:par>\n'
                    '						<p:cTn id="%d" presetID="1" presetClass="entr" presetSubtype="0" fill="hold" grpId="0" nodeType="clickEffect">\n'
                    '							<p:stCondLst>\n'
                    '								<p:cond delay="0"/>\n'
                    '							</p:stCondLst>\n'
                    '							<p:childTnLst>\n'
                    '								<p:set>\n'
                    '									<p:cBhvr>\n'
                    '									<p:cTn id="%d" dur="1" fill="hold">\n'
                    '										<p:stCondLst>\n'
                    '											<p:cond delay="0"/>\n'
                    '										</p:stCondLst>\n'
                    '									</p:cTn>\n'
                    '									<p:tgtEl>\n'
                    '										<p:spTgt spid="%d"/>\n'
                    '									</p:tgtEl>\n'
                    '									<p:attrNameLst>\n'
                    '										<p:attrName>style.visibility</p:attrName>\n'
                    '									</p:attrNameLst>\n'
                    '									</p:cBhvr>\n'
                    '									<p:to>\n'
                    '										<p:strVal val="visible"/>\n'
                    '									</p:to>\n'
                    '								</p:set>\n'
                    '							</p:childTnLst>\n'
                    '						</p:cTn>\n'
                    '					</p:par>\n'
                    '				</p:childTnLst>\n'
                    '				</p:cTn>\n'
                    '			</p:par>\n'
                    '		</p:childTnLst>\n'
                    '	</p:cTn>\n'
                    '</p:par>\n' % (nsdecls('p'), ctnId, ctnId + 1, ctnId + 2, ctnId + 3, shape_id))
        anim = parse_xml(anim_xml)
        first_seq_childTnLst.append(anim)

    @property
    def _next_cTn_id(self):
        """Return the next available unique ID (int) for p:cTn element."""
        cTn_id_strs = self.xpath('/p:sld/p:timing//p:cTn/@id')
        ids = [int(id_str) for id_str in cTn_id_strs]
        print(ids)
        return max(ids) + 1


class CT_TLMediaNodeVideo(BaseOxmlElement):
    """`p:video` element, specifying video media details."""

    _tag_seq = ('p:cMediaNode',)
    cMediaNode = OneAndOnlyOne('p:cMediaNode')
    del _tag_seq
