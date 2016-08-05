package com.dtgrid.filter;

import java.io.IOException;

import javax.servlet.Filter;
import javax.servlet.FilterChain;
import javax.servlet.FilterConfig;
import javax.servlet.ServletException;
import javax.servlet.ServletRequest;
import javax.servlet.ServletResponse;

/**
 * 字符集编码过滤器
 * @author 大连首闻科技有限公司
 * @since 2014-10-22 12:23:00
 */
public class EncodingFilter implements Filter{
	
	/**
	 * 是否启用过滤器
	 */
	private String useEncoding;
	
	/**
	 * 过滤器的字符编码
	 */
	private String encoding;
	
	/**
	 * 初始化过滤器参数
	 */
	public void init(FilterConfig config) throws ServletException {
		useEncoding = config.getInitParameter("useEncoding");
		encoding = config.getInitParameter("encoding");
	}
	
	/**
	 * 执行字符集过滤
	 */
	public void doFilter(ServletRequest request, ServletResponse response,
			FilterChain filterChain) throws IOException, ServletException {
		if("true".equals(this.useEncoding))
			request.setCharacterEncoding(encoding);
		filterChain.doFilter(request, response);
	}
	
	/**
	 * 过滤器销毁
	 */
	public void destroy() {
		useEncoding = null;
		encoding = null;
	}

}
