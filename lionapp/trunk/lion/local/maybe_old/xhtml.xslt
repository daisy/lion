<?xml version="1.0" encoding="UTF-8"?>

<!-- Create the translation sheet for all strings. The output is an XHTML
document. -->

<!-- Input format:

  <strings>
    <s>...</s>
    <s>...</s>
    ...
  </strings>

  -->

<xsl:transform version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:template match="/">
    <html lang="en" xml:lang="en">
      <head>
        <title>AMIS localization sheet</title>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <style type="text/css">
          body { font-size: larger }
          p { line-height: 200% }
        </style>
      </head>
      <body>
        <h1>AMIS localization sheet</h1>
        <p>Language:</p>
        <p>Translators:</p>
        <p>Date:</p>
        <p>Instruction for translators: please provide a translation for the
          following prompts in bold below.</p>
        <xsl:apply-templates/>
      </body>
    </html>
  </xsl:template>

  <xsl:template match="s">
    <p>
      <strong>
        <xsl:value-of select="."/>
      </strong>
      <!--Uncomment for colons-->
	  <!--<xsl:text>:</xsl:text>-->
    </p>
  </xsl:template>

</xsl:transform>
