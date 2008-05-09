<?xml version="1.0" encoding="UTF-8"?>

<!-- Create the translation sheet for all strings. The output is an XSLFO
file that can be transformed into a PDF with FOP. -->

<!-- Input format:

  <strings>
    <s>...</s>
    <s>...</s>
    ...
  </strings>

  -->

<xsl:transform version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:fo="http://www.w3.org/1999/XSL/Format">

  <!-- Prepare the layout for the document. -->

  <xsl:template match="/">
    <fo:root>
      <fo:layout-master-set>
        <fo:simple-page-master master-name="simple-page">
          <fo:region-body margin="20mm"/>
          <fo:region-after extent="20mm" region-name="footer"/>
        </fo:simple-page-master>
      </fo:layout-master-set>
      <fo:page-sequence master-reference="simple-page" font-family="Helvetica"
        font-size="14pt" text-align="justify" leader-pattern="rule"
        leader-length.optimum="100%" rule-thickness=".5pt">
        <!-- Page number in the footer -->
        <fo:static-content flow-name="footer">
          <fo:block text-align="center" margin-top="1em">
            <fo:page-number/>
          </fo:block>
        </fo:static-content>
        <fo:flow flow-name="xsl-region-body">
          <xsl:call-template name="start-page"/>
          <fo:block line-height="2">
            <xsl:apply-templates/>
          </fo:block>
        </fo:flow>
      </fo:page-sequence>
    </fo:root>
  </xsl:template>

  <xsl:template match="s">
    <fo:block>
      <fo:inline font-weight="bold">
        <xsl:value-of select="normalize-space(.)"/>
      </fo:inline>
      <xsl:text>: </xsl:text>
      <xsl:call-template name="make-lines">
        <xsl:with-param name="str" select="."/>
      </xsl:call-template>
    </fo:block>
  </xsl:template>

  <!-- Start a new page -->
  <xsl:template name="start-page">
    <fo:block font-weight="bold" font-size="120%" text-align="center"
      space-after="24pt" break-before="page">
      <xsl:text>Amis localization sheet</xsl:text>
    </fo:block>
    <!-- Space for language, translator(s) and date information -->
    <fo:block line-height="2" space-after="18pt">
      <xsl:text>Language: </xsl:text>
      <xsl:call-template name="make-line"/>
      <xsl:text>Translator(s): </xsl:text>
      <xsl:call-template name="make-line"/>
      <xsl:call-template name="make-line"/>
      <xsl:text>Date: </xsl:text>
      <xsl:call-template name="make-line"/>
    </fo:block>
    <fo:block>
      Instruction for translators: please provide a translation for the
      following prompts in bold below.
    </fo:block>
  </xsl:template>

  <!-- Draw a horizontal line that spans the whole page -->
  <xsl:template name="make-line">
    <fo:leader baseline-shift="-20%"/>
    <fo:block/>
  </xsl:template>

  <!-- Tries to make enough lines for the translators; i.e. 3 lines + one line
  per extra 32 characters -->
  <xsl:template name="make-lines">
    <xsl:param name="str"/>
    <xsl:call-template name="make-line"/>
    <xsl:call-template name="make-line"/>
    <xsl:call-template name="make-line"/>
    <xsl:call-template name="make-more-lines">
      <xsl:with-param name="str" select="$str"/>
    </xsl:call-template>
  </xsl:template>

  <xsl:template name="make-more-lines">
    <xsl:param name="str"/>
    <xsl:if test="string-length($str)&gt;32">
      <xsl:call-template name="make-line"/>
      <xsl:call-template name="make-more-lines">
        <xsl:with-param name="str" select="substring($str,32)"/>
      </xsl:call-template>
    </xsl:if>
  </xsl:template>

</xsl:transform>
