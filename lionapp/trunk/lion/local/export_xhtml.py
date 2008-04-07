XHTML_XSLT = """
<?xml version="1.0" encoding="UTF-8"?>

<xsl:transform version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns="http://www.w3.org/1999/xhtml" xmlns:amis="http://amisproject.org">

  <xsl:output method="xml" version="1.0" encoding="UTF-8"
    doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"
    doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"/>

  <xsl:template match="/amis:ui">
    <html>
      <xsl:copy-of select="@xml:lang"/>
      <xsl:copy-of select="@dir"/>
      <head>
        <title>
          <xsl:value-of select="%(langname)s"/>
        </title>
        <meta http-equiv="Content-type" content="text/html; charset=UTF-8"/>
      </head>
      <body>
        <h1 class="title">
          <xsl:value-of select="%(langname)s"/>
        </h1>
        <xsl:apply-templates/>
      </body>
    </html>
  </xsl:template>

  <xsl:template match="amis:text">
    <h1>
      <xsl:copy-of select="@xml:lang"/>
      <xsl:copy-of select="@dir"/>
      <xsl:value-of select="."/>
    </h1>
  </xsl:template>

  <xsl:template match="text()"/>

</xsl:transform>
"""

def export_xhtml(file, langname):
    """output xhtml"""
    xslt = XSLT_XHTML % langname
    #save xslt to temp directory
    filename = langname + ".xslt"
    xslt_file = open(filename, 'w')
    xslt_file.write(xslt)
    xslt_file.close()
    
    
    